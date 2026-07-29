# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date

from odoo import _, api, fields, models


class RolloutCompetencyTarget(models.Model):
    _name = 'rollout.competency.target'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Rollout Competency Target'
    _order = 'deadline_date, sequence'

    project_id = fields.Many2one(
        'rollout.project', required=True, ondelete='cascade',
    )
    phase_id = fields.Many2one('rollout.phase', string='Phase')
    role_id = fields.Many2one('rollout.role', string='Role')
    name = fields.Char(required=True, string='Target Description', tracking=True)
    sequence = fields.Integer(default=10)

    # ── What ──
    skill_name = fields.Char(string='Skill Name', required=True,
        help='Competency name (e.g. "Odoo CRM", "ISO 9001 Awareness"). '
             'When hr_skills module is installed, rollout_hr bridge adds skill_id field.')
    target_count = fields.Integer(required=True, default=1, string='Target Count')

    # ── When ──
    deadline_date = fields.Date(required=True, string='Deadline', tracking=True)

    # ── Progress (computed) ──
    current_count = fields.Integer(
        compute='_compute_current_count', store=True, string='Current Count',
    )
    gap = fields.Integer(compute='_compute_gap', store=True, string='Gap')
    progress_pct = fields.Float(compute='_compute_gap', store=True, string='Progress %')

    # ── State (computed) ──
    state = fields.Selection([
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('achieved', 'Achieved'),
        ('at_risk', 'At Risk'),
        ('missed', 'Missed'),
    ], compute='_compute_state', store=True, string='Status')

    # ── Strategies ──
    strategy_ids = fields.One2many(
        'rollout.competency.strategy', 'target_id', string='Strategies',
    )

    @api.depends('skill_name')
    def _compute_current_count(self):
        """Count employees with this skill. Requires hr_skills module."""
        EmployeeSkill = self.env.get('hr.employee.skill')
        if not EmployeeSkill:
            for target in self:
                target.current_count = 0
            return
        for target in self:
            domain = [('skill_id.name', '=ilike', target.skill_name)]
            target.current_count = EmployeeSkill.search_count(domain)

    @api.depends('target_count', 'current_count')
    def _compute_gap(self):
        for target in self:
            target.gap = target.target_count - target.current_count
            target.progress_pct = (
                target.current_count / target.target_count * 100
                if target.target_count else 0.0
            )

    @api.depends('gap', 'deadline_date', 'current_count')
    def _compute_state(self):
        today = date.today()
        for target in self:
            if target.gap <= 0:
                target.state = 'achieved'
            elif target.deadline_date and target.deadline_date < today:
                target.state = 'missed'
            elif target.deadline_date and (target.deadline_date - today).days <= 14:
                target.state = 'at_risk'
            elif target.current_count > 0:
                target.state = 'in_progress'
            else:
                target.state = 'planned'
