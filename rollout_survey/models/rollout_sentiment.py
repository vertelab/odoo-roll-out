"""Extend rollout.sentiment with a link to the originating survey input."""

from odoo import models, fields


class RolloutSentiment(models.Model):
    _inherit = 'rollout.sentiment'

    survey_input_id = fields.Many2one(
        'survey.user_input', string='Survey Input',
        ondelete='set null', index=True,
        help='Completed survey input that generated this sentiment entry.')

    _sql_constraints = [
        ('survey_input_unique', 'UNIQUE(survey_input_id)',
         'A survey input can only generate one sentiment entry.'),
    ]
