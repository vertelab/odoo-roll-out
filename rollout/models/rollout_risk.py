"""Rollout Risk — risk register for rollout projects."""

from odoo import models, fields, api


class RolloutRisk(models.Model):
    _name = 'rollout.risk'
    _description = 'Rollout Risk'
    _inherit = ['mail.thread']
    _order = 'risk_score desc, id'

    project_id = fields.Many2one(
        'rollout.project', string='Project', required=True, ondelete='cascade')
    phase_id = fields.Many2one(
        'rollout.phase', string='Phase', ondelete='set null')

    name = fields.Char('Risk Name', required=True, tracking=True)
    description = fields.Text('Description')

    probability = fields.Selection([
        ('1', '1 - Very Low'),
        ('2', '2 - Low'),
        ('3', '3 - Medium'),
        ('4', '4 - High'),
        ('5', '5 - Very High'),
    ], default='1', required=True, string='Probability')
    impact = fields.Selection([
        ('1', '1 - Very Low'),
        ('2', '2 - Low'),
        ('3', '3 - Medium'),
        ('4', '4 - High'),
        ('5', '5 - Very High'),
    ], default='1', required=True, string='Impact')
    risk_score = fields.Integer(
        'Risk Score', compute='_compute_risk_score', store=True)

    mitigation = fields.Text('Mitigation Plan')
    trigger_event = fields.Char('Trigger Event')
    owner_id = fields.Many2one('res.users', string='Owner')

    state = fields.Selection([
        ('identified', 'Identified'),
        ('monitoring', 'Monitoring'),
        ('materialized', 'Materialized'),
        ('mitigated', 'Mitigated'),
    ], default='identified', required=True, tracking=True)

    @api.depends('probability', 'impact')
    def _compute_risk_score(self):
        for risk in self:
            risk.risk_score = int(risk.probability) * int(risk.impact)

    def action_monitor(self):
        self.write({'state': 'monitoring'})

    def action_materialize(self):
        self.write({'state': 'materialized'})

    def action_mitigate(self):
        self.write({'state': 'mitigated'})
