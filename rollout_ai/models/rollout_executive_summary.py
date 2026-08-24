"""Executive Summary — AI-generated weekly summaries for rollout projects.

Stored as ai.company.memory with category='rollout_summary'.
"""

import json
import logging

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class RolloutExecutiveSummary(models.AbstractModel):
    _name = 'rollout.executive.summary'
    _description = 'Rollout Executive Summary Generator'

    @api.model
    def _get_summary(self, project):
        """Generate a markdown executive summary for a rollout project.

        Returns dict: {domain, project_id, period, content, key_metrics, ai_analysis}
        """
        phases = project.phase_ids.sorted('sequence')
        active_phase = phases.filtered(
            lambda p: p.date_start and p.date_end
            and p.date_start <= fields.Date.today() <= p.date_end
        )[:1] or phases[:1]

        # Gather metrics
        total_gap = sum(project.competency_target_ids.mapped('gap') or [0])
        at_risk_targets = project.competency_target_ids.filtered(
            lambda t: t.state == 'at_risk')

        sentiment = project.sentiment_ids.sorted('create_date')
        sentiment_trend = 0.0
        if len(sentiment) >= 2:
            mid = len(sentiment) // 2
            first_avg = sum(s.score for s in sentiment[:mid]) / mid
            second_avg = sum(s.score for s in sentiment[mid:]) / (len(sentiment) - mid)
            sentiment_trend = round(second_avg - first_avg, 2)

        active_risks = project.risk_ids.filtered(
            lambda r: r.state in ('identified', 'monitoring'))
        top_risks = active_risks.sorted('risk_score', reverse=True)[:3]

        # Build markdown content
        content_parts = [
            f'# Rollout Status: {project.name}',
            f'**Period**: Week ending {fields.Date.today()}',
            f'**State**: {project.state} | **Perspective**: {project.perspective}',
            '',
            '## ADKAR Phases',
        ]

        for phase in phases:
            status_icon = '✅' if phase.gate_passed else '🟡' if phase.progress > 0 else '⬜'
            content_parts.append(
                f'- {status_icon} **{phase.adkar_phase}**: '
                f'{phase.progress:.0f}% — {phase.name} '
                f'({phase.date_start} → {phase.date_end})')

        content_parts.extend([
            '',
            '## Competency',
        ])
        for target in project.competency_target_ids:
            risk_mark = '⚠️' if target.state == 'at_risk' else '✅' if target.state == 'achieved' else ''
            content_parts.append(
                f'- {risk_mark} {target.name}: {target.current_count}/{target.target_count} '
                f'(gap: {target.gap}) — deadline: {target.deadline}')

        content_parts.extend([
            '',
            '## Sentiment',
            f'- Trend: {"↑" if sentiment_trend > 0 else "↓" if sentiment_trend < 0 else "→"} '
            f'{sentiment_trend:+.1f} this period',
        ])
        if active_phase:
            avg = sum(s.score for s in project.sentiment_ids.filtered(
                lambda s: s.phase_id == active_phase)[-10:])
            count = len(project.sentiment_ids.filtered(
                lambda s: s.phase_id == active_phase)[-10:])
            if count:
                content_parts.append(
                    f'- Current phase ({active_phase.name}): {avg/count:.1f}/5 '
                    f'({count} entries)')

        content_parts.extend([
            '',
            '## Top Risks',
        ])
        for risk in top_risks:
            content_parts.append(
                f'- 🔴 **{risk.name}** (score: {risk.risk_score}, {risk.state})'
            )

        if not top_risks:
            content_parts.append('- No active risks')

        content = '\n'.join(content_parts)

        # AI analysis (LLM call)
        ai_analysis = self._ai_analyze(project, content, sentiment_trend, at_risk_targets)

        if ai_analysis.get('recommendations'):
            content += '\n\n## AI Recommendations\n'
            for rec in ai_analysis['recommendations']:
                content += f'- {rec}\n'

        return {
            'domain': 'rollout',
            'project_id': project.id,
            'period': 'weekly',
            'content': content,
            'key_metrics': {
                'phase_progress': project.overall_progress,
                'competency_gap': total_gap,
                'sentiment_trend': sentiment_trend,
                'risk_score': project.total_risk_score,
                'at_risk_targets': len(at_risk_targets),
            },
            'ai_analysis': ai_analysis,
        }

    @api.model
    def _ai_analyze(self, project, content, sentiment_trend, at_risk_targets):
        """Generate AI analysis using LLM via ai_agent_core."""
        try:
            llm = self.env['ai.llm']
        except KeyError:
            return {'recommendations': []}

        prompt = (
            f"Given this rollout project summary, identify 1-3 actionable "
            f"recommendations for the project manager.\n\n"
            f"Project: {project.name}\n"
            f"Sentiment trend: {sentiment_trend:+.1f}\n"
            f"At-risk targets: {len(at_risk_targets)}\n"
            f"Active risks: {project.total_risk_score} total score\n\n"
            f"Summary:\n{content[:2000]}\n\n"
            f"Return JSON: {{'recommendations': ['...']}}"
        )

        try:
            result = llm.call(prompt)
            return json.loads(result) if isinstance(result, str) else result
        except Exception as e:
            _logger.warning("rollout_ai: LLM analysis failed: %s", e)
            return {'recommendations': []}


class RolloutProject(models.Model):
    _inherit = 'rollout.project'

    def generate_executive_summary(self):
        """Generate and store an executive summary for this project."""
        self.ensure_one()
        summary_gen = self.env['rollout.executive.summary']
        summary = summary_gen._get_summary(self)

        # Store in ai.company.memory
        if hasattr(self.env, 'ai.company.memory'):
            self.env['ai.company.memory'].create({
                'company_id': self.env.company.id,
                'content': summary['content'],
                'category': 'rollout_summary',
                'importance': 'high',
                'source_ref': f'rollout.project,{self.id}',
            })

        return summary

    def cron_generate_executive_summaries(self):
        """Cron: generate summaries for active projects based on their frequency."""
        today = fields.Date.today()
        projects = self.search([('state', '=', 'active')])
        for project in projects:
            freq = project.executive_summary_frequency or 'weekly'
            if freq == 'weekly' and today.weekday() == 0:  # Monday
                project.generate_executive_summary()
            elif freq == 'biweekly' and today.weekday() == 0 and today.isocalendar()[1] % 2 == 0:
                project.generate_executive_summary()
            elif freq == 'monthly' and today.day == 1:
                project.generate_executive_summary()
