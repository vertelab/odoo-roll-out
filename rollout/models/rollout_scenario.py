"""Rollout Scenario — what-if analysis for rollout timelines."""

from odoo import models, fields


class RolloutScenario(models.Model):
    _name = 'rollout.scenario'
    _description = 'Rollout Scenario'
    _order = 'create_date'

    project_id = fields.Many2one(
        'rollout.project', string='Project', required=True, ondelete='cascade')

    name = fields.Char('Scenario Name', required=True)
    description = fields.Text('Description')

    # Overrides
    override_date_start = fields.Date('Override Start Date')
    override_date_launch = fields.Date('Override Go-Live Date')

    # Assessment
    risk_level = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], string='Risk Level')
    adoption_estimate = fields.Float(
        'Adoption Estimate %', default=80.0)
    cost_estimate = fields.Monetary(
        'Cost Estimate', currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        default=lambda self: self.env.company.currency_id)

    selected = fields.Boolean('Selected as Active Plan')

    # Phase overrides
    phase_override_ids = fields.One2many(
        'rollout.scenario.phase.override', 'scenario_id',
        string='Phase Overrides')

    def action_select(self):
        self.project_id.scenario_ids.write({'selected': False})
        self.write({'selected': True})


class RolloutScenarioPhaseOverride(models.Model):
    _name = 'rollout.scenario.phase.override'
    _description = 'Scenario Phase Duration Override'

    scenario_id = fields.Many2one(
        'rollout.scenario', required=True, ondelete='cascade')
    phase_id = fields.Many2one(
        'rollout.phase', string='Phase', required=True)
    override_duration_days = fields.Integer(
        'Override Duration (days)', required=True)
