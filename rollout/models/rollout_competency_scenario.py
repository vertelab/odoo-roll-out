# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date, timedelta

from odoo import _, api, fields, models


class RolloutCompetencyScenario(models.Model):
    _name = 'rollout.competency.scenario'
    _description = 'Competency Scenario Package'
    _order = 'name'

    project_id = fields.Many2one(
        'rollout.project', required=True, ondelete='cascade',
    )
    name = fields.Char(required=True)
    description = fields.Text()

    # ── Strategies ──
    strategy_ids = fields.One2many(
        'rollout.competency.strategy', 'scenario_id', string='Strategies',
    )

    # ── Computed Totals ──
    total_cost = fields.Monetary(compute='_compute_totals', store=True)
    total_lead_time_days = fields.Integer(
        compute='_compute_totals', store=True, string='Total Lead Time',
    )
    earliest_completion = fields.Date(
        compute='_compute_totals', store=True, string='Earliest Completion',
    )
    risk_level = fields.Selection([
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
    ], compute='_compute_risk', store=True)

    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.company.currency_id,
    )

    # ── Selection ──
    selected = fields.Boolean(default=False, string='Selected Scenario')

    @api.depends('strategy_ids.cost_total', 'strategy_ids.lead_time_days')
    def _compute_totals(self):
        for s in self:
            strategies = s.strategy_ids
            s.total_cost = sum(st.cost_total for st in strategies)
            s.total_lead_time_days = max(
                (st.lead_time_days for st in strategies), default=0,
            )
            today = date.today()
            if s.total_lead_time_days:
                s.earliest_completion = today + timedelta(
                    days=s.total_lead_time_days,
                )

    @api.depends('strategy_ids.strategy_type')
    def _compute_risk(self):
        for s in self:
            types = s.strategy_ids.mapped('strategy_type')
            if 'external' in types and 'training' not in types:
                s.risk_level = 'medium'
            elif 'external_temp' in types:
                s.risk_level = 'low'
            elif 'internal' in types and 'training' in types:
                s.risk_level = 'low'
            elif 'training' in types:
                s.risk_level = 'medium'
            else:
                s.risk_level = 'medium'
