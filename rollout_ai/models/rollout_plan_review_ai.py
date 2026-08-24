"""AI Plan Review — LLM-assisted scoring of rollout plan review criteria."""

import json
import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class RolloutPlanReviewAI(models.AbstractModel):
    _name = 'rollout.plan.review.ai'
    _description = 'AI Plan Review Scoring'

    @api.model
    def suggest_scores(self, review):
        """Generate AI-suggested scores for all criteria in a plan review.

        Returns the review record with ai_suggestion fields populated.
        """
        project = review.project_id
        criteria = self.env['rollout.plan.review.criteria'].search([])

        # Build project data context
        context = self._build_project_context(project)

        for criterion in criteria:
            try:
                score_data = self._suggest_score(criterion, context)
            except Exception as e:
                _logger.warning("rollout_ai: Score suggestion failed for %s: %s",
                                criterion.name, e)
                continue

            # Find or create score record
            score_record = review.criteria_score_ids.filtered(
                lambda s: s.criteria_id == criterion)
            if not score_record:
                score_record = self.env['rollout.plan.review.criteria.score'].create({
                    'review_id': review.id,
                    'criteria_id': criterion.id,
                    'score': 0,
                })

            score_record.write({
                'ai_suggested': True,
                'ai_suggestion': score_data.get('score', 0),
                'ai_confidence': score_data.get('confidence', 0.5),
                'justification': score_data.get('justification', ''),
                'score': score_data.get('score', 0),  # Pre-fill score
            })

        return review

    @api.model
    def batch_suggest_scores(self, review):
        """Generate AI suggestions for all 42 criteria in one operation."""
        return self.suggest_scores(review)

    @api.model
    def _suggest_score(self, criterion, context):
        """Suggest a score for a single criterion using LLM.

        Returns {score, confidence, justification}.
        """
        try:
            llm = self.env['ai.llm']
        except KeyError:
            return {'score': 0, 'confidence': 0.0,
                    'justification': 'AI service not available'}

        prompt = (
            f"Score this plan review criterion on a scale of 0-{criterion.max_score} "
            f"based on the project data provided.\n\n"
            f"Criterion: {criterion.name}\n"
            f"Dimension: {criterion.dimension}\n"
            f"Description: {criterion.description or 'N/A'}\n"
            f"Max score: {criterion.max_score}\n\n"
            f"Project Data:\n{context[:2000]}\n\n"
            f"Return JSON: {{\n"
            f'  "score": <0-{criterion.max_score}>,\n'
            f'  "confidence": <0.0-1.0>,\n'
            f'  "justification": "<1 sentence explaining the score>"\n'
            f'}}'
        )

        try:
            result = llm.call(prompt)
            return json.loads(result) if isinstance(result, str) else result
        except Exception as e:
            _logger.warning("rollout_ai: LLM call failed: %s", e)
            return {'score': 0, 'confidence': 0.0,
                    'justification': f'LLM error: {e}'}

    @api.model
    def _build_project_context(self, project):
        """Build a text summary of project data for AI scoring context."""
        parts = [
            f'Project: {project.name}',
            f'State: {project.state}',
            f'Perspective: {project.perspective}',
            f'Overall Progress: {project.overall_progress:.0f}%',
            f'Total Competency Gap: {project.total_competency_gap}',
            f'Total Risk Score: {project.total_risk_score}',
            '',
            'Phases:',
        ]
        for phase in project.phase_ids:
            parts.append(
                f'  - {phase.adkar_phase}: {phase.name} '
                f'({phase.progress:.0f}%, gate: {phase.gate_type})')

        parts.append('\nCompetency Targets:')
        for target in project.competency_target_ids:
            parts.append(
                f'  - {target.name}: {target.current_count}/{target.target_count} '
                f'(gap: {target.gap}, state: {target.state})')

        parts.append('\nRoles:')
        for role in project.role_ids:
            parts.append(
                f'  - {role.name}: {len(role.employee_ids)} employees, '
                f'{len(role.required_skill_ids)} skills required')

        parts.append('\nRisks:')
        for risk in project.risk_ids.filtered(
                lambda r: r.state in ('identified', 'monitoring')):
            parts.append(f'  - {risk.name} (score: {risk.risk_score})')

        return '\n'.join(parts)


class RolloutPlanReview(models.Model):
    _inherit = 'rollout.plan.review'

    def action_ai_suggest_scores(self):
        """Button: generate AI suggestions for all criteria."""
        ai = self.env['rollout.plan.review.ai']
        ai.suggest_scores(self)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
