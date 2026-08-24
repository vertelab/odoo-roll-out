"""AI Sentiment Analysis - LLM hotspot detection for rollout sentiment comments.

Uses ai.coworker.run() as the LLM bridge (ai_agent_core). Falls back to
keyword-based detection when no coworker/agent is available or the LLM call
fails, so the module degrades gracefully.
"""

import json
import logging
import re

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class RolloutSentimentAI(models.AbstractModel):
    _name = 'rollout.sentiment.ai'
    _description = 'AI Sentiment Analysis for Rollout'

    @api.model
    def detect_hotspots(self, project):
        """Analyze sentiment free-text comments for hotspots using LLM.

        Returns list of hotspot dicts: {department, topic, confidence, phrases}
        """
        comments = project.sentiment_ids.filtered(
            lambda s: s.comment and not s.hotspot_detected)
        if len(comments) < 3:
            return []

        # Try LLM first
        try:
            return self._llm_detect_hotspots(project, comments)
        except Exception as e:
            _logger.warning("rollout_ai: LLM hotspot detection failed: %s", e)
            return self._keyword_detect_hotspots(comments)

    @api.model
    def _llm_detect_hotspots(self, project, comments):
        """Use ai.coworker.run() (ai_agent_core) to detect sentiment hotspots."""
        try:
            coworker = self.env['ai.coworker'].search(
                [('active', '=', True)], limit=1)
            if not coworker:
                _logger.info("rollout_ai: no ai.coworker found, keyword fallback")
                return self._keyword_detect_hotspots(comments)
        except KeyError:
            return self._keyword_detect_hotspots(comments)

        comment_text = '\n'.join(
            f'- [{c.create_date}] (score {c.score}): {c.comment[:300]}'
            for c in comments[-50:]
        )

        prompt = (
            f"Analyze these sentiment comments from a rollout project "
            f"and identify any hotspots - departments, topics, or roles "
            f"with declining or negative sentiment patterns.\n\n"
            f"Project: {project.name}\n\n"
            f"Comments:\n{comment_text[:3000]}\n\n"
            f"Return JSON only:\n"
            f"{{\n"
            f'  "hotspots": [\n'
            f'    {{"department": "...", "topic": "...", '
            f'"confidence": 0.0-1.0, "phrases": ["..."]}}\n'
            f'  ]\n'
            f"}}\n"
        )

        try:
            result = coworker.run(prompt=prompt)
            if not result:
                _logger.info("rollout_ai: empty coworker response, keyword fallback")
                return self._keyword_detect_hotspots(comments)

            data = self._parse_json_response(result)
            if not data or not isinstance(data, dict):
                return self._keyword_detect_hotspots(comments)

            hotspots = data.get('hotspots', []) or []
            for hotspot in hotspots:
                if hotspot.get('confidence', 0) >= 0.5:
                    matching = comments.filtered(
                        lambda c: any(
                            phrase.lower() in (c.comment or '').lower()
                            for phrase in hotspot.get('phrases', [])
                        )
                    )
                    matching.write({
                        'hotspot_detected': True,
                        'hotspot_department': hotspot.get('department', ''),
                        'hotspot_topic': hotspot.get('topic', ''),
                        'hotspot_confidence': hotspot.get('confidence', 0.0),
                    })
            return hotspots
        except Exception as e:
            _logger.warning("rollout_ai: LLM call failed: %s", e)
            return self._keyword_detect_hotspots(comments)

    @api.model
    def _parse_json_response(self, result):
        """Robustly extract JSON from LLM output (handles markdown fences)."""
        text = str(result).strip()
        # Strip markdown code fences
        fence = re.search(r'```(?:json)?\s*(.*?)```', text, re.S)
        if fence:
            text = fence.group(1).strip()
        try:
            return json.loads(text)
        except (ValueError, TypeError):
            pass
        # Fall back to the first balanced {...} block
        match = re.search(r'\{.*\}', text, re.S)
        if match:
            try:
                return json.loads(match.group(0))
            except (ValueError, TypeError):
                pass
        return None

    @api.model
    def _keyword_detect_hotspots(self, comments):
        """Fallback: keyword-based hotspot detection."""
        negative_keywords = [
            'svårt', 'förvirrande', 'frustrerande', 'osäkert',
            'jobbigt', 'krångligt', 'otydligt', 'stressigt',
            'förstår inte', 'hjälp', 'problem',
        ]
        keyword_matches = comments.filtered(
            lambda c: any(
                kw in (c.comment or '').lower()
                for kw in negative_keywords
            )
        )
        hotspots = []
        if keyword_matches:
            hotspots.append({
                'department': 'unknown',
                'topic': 'general',
                'confidence': 0.5,
                'phrases': negative_keywords[:5],
            })
            keyword_matches.write({
                'hotspot_detected': True,
                'hotspot_confidence': 0.5,
            })
        return hotspots

    @api.model
    def analyze_project(self, project):
        """Run hotspot detection for a project and post a summary to chatter."""
        hotspots = self.detect_hotspots(project)
        if not hotspots:
            return []
        summary = '\n'.join(
            '- {topic} ({department}, conf {confidence})'.format(
                topic=h.get('topic', '?'),
                department=h.get('department', 'unknown'),
                confidence=h.get('confidence', 0.0))
            for h in hotspots
        )
        project.message_post(
            body='AI sentiment analysis detected hotspots:\n%s' % summary)
        return hotspots

    @api.model
    def compare_trends(self, project, weeks=2):
        """Compare sentiment between current and previous periods."""
        entries = project.sentiment_ids.sorted('create_date')
        if len(entries) < 4:
            return {'significant_decline': False}

        mid = len(entries) // 2
        old_avg = sum(e.score for e in entries[:mid]) / mid
        new_avg = sum(e.score for e in entries[mid:]) / (len(entries) - mid)
        decline = new_avg < old_avg - 0.5

        return {
            'old_avg': round(old_avg, 1),
            'new_avg': round(new_avg, 1),
            'change': round(new_avg - old_avg, 2),
            'significant_decline': decline,
        }
