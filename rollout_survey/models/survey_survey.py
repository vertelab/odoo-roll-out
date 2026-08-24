"""Extend survey.survey with rollout OBMS fields + sentiment generation."""

from odoo import models, fields


class SurveySurvey(models.Model):
    _inherit = 'survey.survey'

    rollout_project_id = fields.Many2one(
        'rollout.project', string='Rollout Project', ondelete='set null')
    rollout_phase_id = fields.Many2one(
        'rollout.phase', string='Rollout Phase', ondelete='set null',
        help='Phase this pulse belongs to. Defaults to the project first phase.')
    rollout_dimension = fields.Selection([
        ('structure', 'Structure'),
        ('culture', 'Culture'),
        ('behavior', 'Behaviour'),
    ], string='OBMS Dimension')
    rollout_wave = fields.Selection([
        ('baseline', 'Baseline'),
        ('midline', 'Midline'),
        ('endline', 'Endline'),
    ], default='baseline', string='Pulse Wave')
    rollout_survey_type = fields.Selection([
        ('obms', 'OBMS Pulse'),
        ('sentiment', 'Sentiment Pulse'),
        ('custom', 'Custom'),
    ], default='obms', string='Rollout Type')
    rollout_active = fields.Boolean(
        'Generate Sentiment', default=True,
        help='Generate rollout.sentiment entries from completed inputs.')

    def action_generate_sentiment(self):
        """Generate idempotent rollout.sentiment entries for all done inputs."""
        self.ensure_one()
        if not self.rollout_project_id or not self.rollout_active:
            return False

        inputs = self.user_input_ids.filtered(
            lambda i: i.state == 'done' and not i.test_entry)
        created = 0
        for user_input in inputs:
            if self.env['rollout.sentiment'].search_count(
                    [('survey_input_id', '=', user_input.id)]):
                continue
            vals = user_input._prepare_rollout_sentiment_values()
            if vals:
                self.env['rollout.sentiment'].create(vals)
                created += 1

        if created:
            self.message_post(
                body='Generated %s rollout sentiment entries.' % created)
        return True
