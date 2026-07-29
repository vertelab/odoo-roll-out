# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class RolloutScenario(models.Model):
    _name = 'rollout.scenario'
    _description = 'Rollout Scenario'
    _order = 'name'

    project_id = fields.Many2one(
        'rollout.project', required=True, ondelete='cascade',
    )
    name = fields.Char(required=True)
    description = fields.Text()

    # ── Overrides ──
    override_date_start = fields.Date(string='Override Start Date')
    override_date_launch = fields.Date(string='Override Go-Live Date')

    # ── Phase Adjustments ──
    phase_adjustment_ids = fields.One2many(
        'rollout.scenario.phase_adjustment', 'scenario_id',
        string='Phase Adjustments',
    )

    # ── Assessment ──
    risk_level = fields.Selection([
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
    ])
    adoption_estimate = fields.Float(string='Estimated Adoption (%)')
    cost_estimate = fields.Monetary(string='Estimated Cost')
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.company.currency_id,
    )

    # ── Selection ──
    selected = fields.Boolean(default=False, string='Selected Scenario')


class RolloutScenarioPhaseAdjustment(models.Model):
    _name = 'rollout.scenario.phase_adjustment'
    _description = 'Scenario Phase Duration Adjustment'
    _order = 'sequence'

    scenario_id = fields.Many2one(
        'rollout.scenario', required=True, ondelete='cascade',
    )
    phase_id = fields.Many2one('rollout.phase', required=True, string='Phase')
    override_duration_days = fields.Integer(string='Override Duration (Days)')
    sequence = fields.Integer(related='phase_id.sequence', store=True)
