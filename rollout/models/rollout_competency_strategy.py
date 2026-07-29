# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class RolloutCompetencyStrategy(models.Model):
    _name = 'rollout.competency.strategy'
    _description = 'Competency Strategy'
    _order = 'sequence, id'

    target_id = fields.Many2one(
        'rollout.competency.target', required=True, ondelete='cascade',
    )
    scenario_id = fields.Many2one(
        'rollout.competency.scenario', string='Scenario Package',
    )
    name = fields.Char(required=True, string='Strategy Name')
    sequence = fields.Integer(default=10)

    # ── Type ──
    strategy_type = fields.Selection([
        ('internal', 'Internal Reassignment'),
        ('external', 'External Recruitment'),
        ('training', 'Training / Development'),
        ('external_temp', 'Consultant / Temporary'),
    ], required=True, string='Strategy Type')

    # ── Targets ──
    planned_count = fields.Integer(default=1, string='Planned Count')
    achieved_count = fields.Integer(default=0, string='Achieved Count')

    # ── Cost ──
    cost_per_person = fields.Monetary(string='Cost per Person')
    cost_total = fields.Monetary(compute='_compute_cost', store=True)
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.company.currency_id,
    )

    # ── Time ──
    lead_time_days = fields.Integer(default=30, string='Lead Time (Days)')

    # ── State ──
    state = fields.Selection([
        ('planned', 'Planned'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ], default='planned')

    # ── Links (optional — require respective modules) ──
    # job_id is added by rollout_hr bridge when hr_recruitment is installed
    # course_ids is added by rollout_lms bridge when website_slides is installed
    course_name = fields.Char(string='Training Course Name',
        help='Course name. When website_slides is installed, rollout_lms bridge adds course_ids field.')

    @api.depends('cost_per_person', 'planned_count')
    def _compute_cost(self):
        for s in self:
            s.cost_total = s.cost_per_person * s.planned_count
