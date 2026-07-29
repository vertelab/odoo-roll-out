# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class RolloutProject(models.Model):
    _name = 'rollout.project'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Rollout Project'

    name = fields.Char(required=True, tracking=True)
    active = fields.Boolean(default=True)
    customer_id = fields.Many2one(
        'res.partner', required=True, string='Customer', tracking=True,
        domain=[('is_company', '=', True)],
    )
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.company,
    )

    # ── Project Organization ──
    project_manager_id = fields.Many2one(
        'res.users', string='Project Manager', tracking=True,
    )
    team_member_ids = fields.Many2many(
        'res.users', 'rollout_project_team_rel',
        'project_id', 'user_id', string='Project Team',
    )
    sponsor_id = fields.Many2one(
        'res.partner', string='Change Sponsor (Customer)', tracking=True,
    )

    # ── State ──
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='draft', tracking=True)

    # ── Timeline ──
    planning_mode = fields.Selection([
        ('forward', 'Forward: Start date → compute go-live'),
        ('backward', 'Backward: Go-live date → compute start'),
    ], required=True, default='backward', tracking=True)
    date_start = fields.Date(string='Start Date', tracking=True)
    date_launch = fields.Date(string='Go-Live Date', tracking=True)

    # ── Relations ──
    phase_ids = fields.One2many('rollout.phase', 'project_id', string='Phases')
    risk_ids = fields.One2many('rollout.risk', 'project_id', string='Risks')
    scenario_ids = fields.One2many('rollout.scenario', 'project_id', string='Scenarios')
    sentiment_ids = fields.One2many('rollout.sentiment', 'project_id', string='Sentiment')
    nudge_ids = fields.One2many('rollout.nudge', 'project_id', string='Nudges')
    org_change_ids = fields.One2many(
        'rollout.org_change', 'project_id', string='Organizational Changes',
    )
    competency_target_ids = fields.One2many(
        'rollout.competency.target', 'project_id', string='Competency Targets',
    )
    review_ids = fields.One2many(
        'rollout.plan.review', 'project_id', string='Plan Reviews',
    )

    # ── Computed ──
    phase_count = fields.Integer(compute='_compute_counts', string='Phases')
    risk_count = fields.Integer(compute='_compute_counts', string='Risks')
    target_count = fields.Integer(compute='_compute_counts', string='Competency Targets')

    @api.depends('phase_ids', 'risk_ids', 'competency_target_ids')
    def _compute_counts(self):
        for r in self:
            r.phase_count = len(r.phase_ids)
            r.risk_count = len(r.risk_ids)
            r.target_count = len(r.competency_target_ids)

    def action_activate(self):
        self.ensure_one()
        self.state = 'active'

    def action_complete(self):
        self.ensure_one()
        self.state = 'completed'

    def action_cancel(self):
        self.ensure_one()
        self.state = 'cancelled'
