"""Rollout Competency Target — skill targets for a rollout phase."""

from odoo import models, fields, api, _


class RolloutCompetencyTarget(models.Model):
    _name = 'rollout.competency.target'
    _description = 'Rollout Competency Target'
    _order = 'deadline, id'

    project_id = fields.Many2one(
        'rollout.project', string='Project', required=True, ondelete='cascade')
    phase_id = fields.Many2one(
        'rollout.phase', string='Phase', ondelete='set null')
    role_id = fields.Many2one(
        'rollout.role', string='Target Role', ondelete='set null')

    name = fields.Char('Target Name', required=True)
    skill_id = fields.Many2one(
        'hr.skill', string='Skill', help='Competency skill from HR')
    level = fields.Char('Required Level')
    target_count = fields.Integer('Target Count', default=1, required=True)
    current_count = fields.Integer(
        'Current Count', compute='_compute_current_count', store=True)
    gap = fields.Integer('Gap', compute='_compute_gap', store=True)
    progress_pct = fields.Float(
        'Progress %', compute='_compute_progress_pct', store=True)
    deadline = fields.Date('Deadline', required=True)

    state = fields.Selection([
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('at_risk', 'At Risk'),
        ('achieved', 'Achieved'),
        ('missed', 'Missed'),
    ], compute='_compute_state', store=True, default='planned')

    @api.depends('skill_id', 'level')
    def _compute_current_count(self):
        for target in self:
            if not target.skill_id:
                target.current_count = 0
                continue
            # Count employees with this skill at or above the required level
            # Requires hr_skill module integration
            # For standalone: count is maintained manually or via bridges
            target.current_count = 0  # Base value, updated by bridges

    @api.depends('target_count', 'current_count')
    def _compute_gap(self):
        for target in self:
            target.gap = max(0, target.target_count - target.current_count)

    @api.depends('target_count', 'current_count')
    def _compute_progress_pct(self):
        for target in self:
            target.progress_pct = (
                min(100.0, (target.current_count / target.target_count) * 100)
                if target.target_count > 0 else 100.0)

    @api.depends('gap', 'deadline', 'current_count')
    def _compute_state(self):
        today = fields.Date.context_today(self)
        for target in self:
            if target.gap <= 0:
                target.state = 'achieved'
            elif target.deadline and target.deadline < today:
                target.state = 'missed'
            elif (target.deadline
                  and (target.deadline - today).days <= 14
                  and target.gap > 0):
                target.state = 'at_risk'
            elif target.current_count > 0:
                target.state = 'in_progress'
            else:
                target.state = 'planned'
