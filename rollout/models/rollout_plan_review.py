# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class RolloutPlanReview(models.Model):
    _name = 'rollout.plan.review'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Multi-Dimensional Plan Review'

    project_id = fields.Many2one(
        'rollout.project', required=True, ondelete='cascade',
    )
    name = fields.Char(compute='_compute_name', store=True)
    reviewer_id = fields.Many2one(
        'res.users', required=True, string='Reviewer',
        default=lambda self: self.env.user,
    )
    review_date = fields.Datetime(default=fields.Datetime.now)

    # ── Scope ──
    scenario_id = fields.Many2one(
        'rollout.scenario', string='Reviewing Scenario',
    )

    # ── State ──
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ], default='draft', tracking=True)

    # ── Dimensions ──
    dimension_ids = fields.One2many(
        'rollout.plan.review.dimension', 'review_id', string='Dimensions',
    )

    # ── Overall Score ──
    overall_score = fields.Float(
        compute='_compute_overall', store=True, string='Overall Score (0-100)',
    )
    overall_rating = fields.Selection([
        ('critical', '🔴 Critical'),
        ('weak', '🟠 Weak'),
        ('adequate', '🟡 Adequate'),
        ('strong', '🟢 Strong'),
        ('excellent', '⭐ Excellent'),
    ], compute='_compute_overall', store=True)

    # ── Summary ──
    summary = fields.Html(string='Summary')
    recommendations = fields.Html(string='Recommendations')

    # ── Approval ──
    approval_required = fields.Boolean(default=True)
    approved_by_id = fields.Many2one('res.users', string='Approved By')

    @api.depends('project_id', 'scenario_id', 'review_date')
    def _compute_name(self):
        for r in self:
            base = f'Review: {r.project_id.name}'
            if r.scenario_id:
                base += f' — Scenario: {r.scenario_id.name}'
            date_str = r.review_date.strftime('%Y-%m-%d') if r.review_date else ''
            r.name = f'{base} ({date_str})'

    @api.depends('dimension_ids.score')
    def _compute_overall(self):
        for r in self:
            dims = r.dimension_ids
            if not dims:
                r.overall_score = 0.0
                r.overall_rating = 'critical'
                continue
            r.overall_score = sum(d.score for d in dims) / len(dims)
            if r.overall_score >= 90:
                r.overall_rating = 'excellent'
            elif r.overall_score >= 75:
                r.overall_rating = 'strong'
            elif r.overall_score >= 60:
                r.overall_rating = 'adequate'
            elif r.overall_score >= 40:
                r.overall_rating = 'weak'
            else:
                r.overall_rating = 'critical'

    def action_start_review(self):
        self.ensure_one()
        self.state = 'in_progress'

    def action_complete(self):
        self.ensure_one()
        self.state = 'completed'

    def action_approve(self):
        self.ensure_one()
        self.approved_by_id = self.env.user


class RolloutPlanReviewDimension(models.Model):
    _name = 'rollout.plan.review.dimension'
    _description = 'Review Dimension'
    _order = 'sequence, id'

    review_id = fields.Many2one(
        'rollout.plan.review', required=True, ondelete='cascade',
    )
    sequence = fields.Integer(default=10)

    # ── Dimension ──
    dimension = fields.Selection([
        ('behavioral', '🧠 Behavioral Science'),
        ('risk', '⚠️ Risk Management'),
        ('competency', '👥 Competency Planning'),
        ('timeline', '📅 Timeline & Resources'),
        ('stakeholder', '👤 Stakeholders & Communication'),
        ('iso_compliance', '📋 ISO / Compliance'),
        ('org_change', '🏢 Organizational Change'),
        ('budget', '💰 Budget & Costs'),
        ('training', '📚 Training & LMS'),
    ], required=True)

    # ── Scoring ──
    score = fields.Float(string='Score (0-100)')
    rating = fields.Selection([
        ('critical', '🔴 Critical'),
        ('weak', '🟠 Weak'),
        ('adequate', '🟡 Adequate'),
        ('strong', '🟢 Strong'),
        ('excellent', '⭐ Excellent'),
    ], compute='_compute_rating', store=True)

    # ── SWOT ──
    strengths = fields.Html(string='Strengths')
    weaknesses = fields.Html(string='Weaknesses')
    opportunities = fields.Html(string='Opportunities')
    threats = fields.Html(string='Threats')

    # ── Criteria ──
    criterion_ids = fields.One2many(
        'rollout.plan.review.criterion', 'dimension_id', string='Criteria',
    )

    @api.depends('score')
    def _compute_rating(self):
        for d in self:
            if d.score >= 90:
                d.rating = 'excellent'
            elif d.score >= 75:
                d.rating = 'strong'
            elif d.score >= 60:
                d.rating = 'adequate'
            elif d.score >= 40:
                d.rating = 'weak'
            else:
                d.rating = 'critical'


class RolloutPlanReviewCriterion(models.Model):
    _name = 'rollout.plan.review.criterion'
    _description = 'Review Criterion'
    _order = 'sequence, id'

    dimension_id = fields.Many2one(
        'rollout.plan.review.dimension', ondelete='cascade',
    )
    sequence = fields.Integer(default=10)
    name = fields.Char(required=True, translate=True, string='Criterion')
    description = fields.Text(translate=True, string='What to Review')

    # ── Assessment ──
    score = fields.Selection([
        ('0', '0 — Completely Missing'),
        ('1', '1 — Inadequate'),
        ('2', '2 — Partially'),
        ('3', '3 — Sufficient'),
        ('4', '4 — Well Developed'),
        ('5', '5 — Excellent'),
    ], string='Assessment')

    finding = fields.Text(string='Finding / Comment')
    action_required = fields.Boolean(string='Action Required?')
