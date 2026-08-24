"""Rollout Project — central model for managing an Odoo rollout implementation."""

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class RolloutProject(models.Model):
    _name = 'rollout.project'
    _description = 'Rollout Project'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    # -- Identification --
    name = fields.Char('Project Name', required=True, tracking=True)
    customer_id = fields.Many2one(
        'res.partner', string='Customer', required=True, tracking=True,
        domain=[('is_company', '=', True)])
    manager_id = fields.Many2one(
        'res.users', string='Project Manager', tracking=True,
        default=lambda self: self.env.user)
    sponsor_id = fields.Many2one(
        'res.partner', string='Change Sponsor', tracking=True,
        help='Sponsor from the customer organization')
    team_member_ids = fields.Many2many(
        'res.users', string='Team Members')

    # -- Timeline --
    planning_mode = fields.Selection([
        ('forward', 'Forward (from start)'),
        ('backward', 'Backward (from go-live)'),
    ], default='backward', required=True, tracking=True)
    date_start = fields.Date('Start Date', tracking=True)
    date_launch = fields.Date('Go-Live Date', tracking=True)

    # -- State --
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('migrated', 'Migrated'),
    ], default='draft', required=True, tracking=True)

    # -- Perspective --
    perspective = fields.Selection([
        ('external', 'External (Consultant)'),
        ('internal', 'Internal (Organization)'),
    ], default='external', required=True, tracking=True)

    # -- Migration --
    migration_state = fields.Selection([
        ('none', 'Never Migrated'),
        ('migrated', 'Migrated to Customer'),
        ('imported', 'Imported from Consultant'),
    ], default='none', readonly=True, tracking=True)
    migrated_from = fields.Char('Migrated From', readonly=True)
    migrated_at = fields.Datetime('Migrated At', readonly=True)

    # -- Relations --
    phase_ids = fields.One2many('rollout.phase', 'project_id', string='ADKAR Phases')
    risk_ids = fields.One2many('rollout.risk', 'project_id', string='Risks')
    sentiment_ids = fields.One2many('rollout.sentiment', 'project_id', string='Sentiment Entries')
    scenario_ids = fields.One2many('rollout.scenario', 'project_id', string='Scenarios')
    competency_target_ids = fields.One2many(
        'rollout.competency.target', 'project_id', string='Competency Targets')
    role_ids = fields.One2many('rollout.role', 'project_id', string='Roles')
    org_change_ids = fields.One2many(
        'rollout.org.change', 'project_id', string='Organizational Changes')
    plan_review_ids = fields.One2many(
        'rollout.plan.review', 'project_id', string='Plan Reviews')
    nudge_ids = fields.One2many('rollout.nudge', 'project_id', string='Nudges')

    # -- Computed metrics --
    overall_progress = fields.Float(
        'Overall Progress %', compute='_compute_overall_progress', store=True)
    total_competency_gap = fields.Integer(
        'Total Competency Gap', compute='_compute_total_competency_gap', store=True)
    sentiment_trend = fields.Float(
        'Sentiment Trend', compute='_compute_sentiment_trend')
    total_risk_score = fields.Integer(
        'Total Risk Score', compute='_compute_total_risk_score', store=True)

    _sql_constraints = [
        ('check_name_not_empty', 'CHECK(char_length(name) > 0)',
         'Project name cannot be empty'),
    ]

    @api.depends('phase_ids.progress')
    def _compute_overall_progress(self):
        for project in self:
            phases = project.phase_ids
            project.overall_progress = (
                sum(p.progress for p in phases) / len(phases)
                if phases else 0.0)

    @api.depends('competency_target_ids.gap')
    def _compute_total_competency_gap(self):
        for project in self:
            project.total_competency_gap = sum(
                project.competency_target_ids.mapped('gap') or [0])

    def _compute_sentiment_trend(self):
        for project in self:
            entries = project.sentiment_ids.sorted('create_date')
            if len(entries) < 2:
                project.sentiment_trend = 0.0
                continue
            recent = entries[-10:] if len(entries) >= 10 else entries
            mid = len(recent) // 2
            first_half_avg = sum(e.score for e in recent[:mid]) / mid
            second_half_avg = sum(e.score for e in recent[mid:]) / (len(recent) - mid)
            project.sentiment_trend = round(second_half_avg - first_half_avg, 2)

    @api.depends('risk_ids.risk_score')
    def _compute_total_risk_score(self):
        for project in self:
            project.total_risk_score = sum(
                project.risk_ids.filtered(
                    lambda r: r.state in ('identified', 'monitoring')
                ).mapped('risk_score') or [0])

    def action_activate(self):
        if not self.phase_ids:
            raise ValidationError(_('At least one phase is required to activate.'))
        self.write({'state': 'active'})
        self.phase_ids._compute_dates()

    def action_complete(self):
        self.write({'state': 'completed'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_mark_migrated(self, migrated_to_url=False):
        self.write({
            'state': 'migrated',
            'migration_state': 'migrated',
            'migrated_at': fields.Datetime.now(),
        })
        if migrated_to_url:
            self.message_post(
                body=_('Project migrated to: %s', migrated_to_url))
