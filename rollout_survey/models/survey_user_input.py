"""Extend survey.user_input with rollout sentiment generation helpers."""

from odoo import models, fields


class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    rollout_sentiment_ids = fields.One2many(
        'rollout.sentiment', 'survey_input_id', string='Rollout Sentiment')

    def _prepare_rollout_sentiment_values(self):
        """Map survey answers -> rollout.sentiment values.

        Scale answers (1-5) become the score (average, rounded to int).
        Text answers become the comment.
        """
        self.ensure_one()
        survey = self.survey_id
        project = survey.rollout_project_id
        if not project:
            return {}

        scores = []
        comments = []
        for line in self.user_input_line_ids:
            if line.skipped:
                continue
            if line.answer_type == 'scale' and line.value_scale:
                scores.append(max(1, min(5, line.value_scale)))
            elif line.answer_type in ('text_box', 'char_box'):
                text = line.value_text_box or line.value_char_box or ''
                if text.strip():
                    comments.append(text.strip())

        if not scores:
            # No scale answers: nothing to score
            return {}

        user = self.partner_id.user_ids[:1]
        phase = survey.rollout_phase_id or (
            project.phase_ids[:1] if project.phase_ids else False)
        score = round(sum(scores) / len(scores))

        return {
            'project_id': project.id,
            'phase_id': phase.id if phase else False,
            'user_id': user.id if user else self.env.user.id,
            'score': score,
            'comment': '\n'.join(comments) if comments else False,
            'dimension': survey.rollout_dimension,
            'wave': survey.rollout_wave,
            'survey_input_id': self.id,
        }
