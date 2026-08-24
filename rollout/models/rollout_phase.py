"""Rollout Phase — ADKAR phase within a rollout project."""

from odoo import models, fields, api, _
from datetime import timedelta


class RolloutPhase(models.Model):
    _name = 'rollout.phase'
    _description = 'Rollout Phase (ADKAR)'
    _order = 'sequence, id'

    project_id = fields.Many2one(
        'rollout.project', string='Project', required=True, ondelete='cascade')
    sequence = fields.Integer('Sequence', default=10)
    name = fields.Char('Phase Name', required=True)

    adkar_phase = fields.Selection([
        ('awareness', 'Awareness'),
        ('desire', 'Desire'),
        ('knowledge', 'Knowledge'),
        ('ability', 'Ability'),
        ('reinforcement', 'Reinforcement'),
    ], required=True, string='ADKAR Phase')

    duration_days = fields.Integer('Duration (days)', default=14, required=True)

    # -- Gate --
    gate_type = fields.Selection([
        ('none', 'No Gate'),
        ('approval', 'Approval'),
        ('metric', 'Metric'),
        ('completion', 'Completion'),
    ], default='none', string='Gate Type')
    gate_metric = fields.Float('Gate Metric (%)', default=80.0)
    gate_passed = fields.Boolean('Gate Passed', compute='_compute_gate_passed', store=True)

    # -- Computed dates --
    date_start = fields.Date('Start Date', compute='_compute_dates', store=True)
    date_end = fields.Date('End Date', compute='_compute_dates', store=True)
    progress = fields.Float('Progress %', compute='_compute_progress')

    # -- Relations --
    competency_target_ids = fields.One2many(
        'rollout.competency.target', 'phase_id', string='Competency Targets')
    sentiment_ids = fields.One2many(
        'rollout.sentiment', 'phase_id', string='Sentiment Entries')
    nudge_ids = fields.One2many(
        'rollout.nudge', 'phase_id', string='Nudges')
    org_change_ids = fields.One2many(
        'rollout.org.change', 'phase_id', string='Organizational Changes')
    preceding_phase_id = fields.Many2one(
        'rollout.phase', string='Preceding Phase',
        compute='_compute_preceding_phase', store=True)

    @api.depends('sequence', 'project_id.phase_ids')
    def _compute_preceding_phase(self):
        for phase in self:
            phases = phase.project_id.phase_ids.sorted('sequence')
            idx = list(phases).index(phase) if phase in phases else -1
            phase.preceding_phase_id = phases[idx - 1] if idx > 0 else False

    @api.depends('gate_type', 'preceding_phase_id.gate_passed')
    def _compute_gate_passed(self):
        for phase in self:
            if not phase.preceding_phase_id:
                phase.gate_passed = True
            elif phase.preceding_phase_id.gate_type == 'none':
                phase.gate_passed = True
            elif phase.preceding_phase_id.gate_type == 'completion':
                phase.gate_passed = phase.preceding_phase_id.progress >= 100
            else:
                phase.gate_passed = False

    @api.depends('project_id.planning_mode', 'project_id.date_start',
                 'project_id.date_launch', 'duration_days', 'sequence',
                 'project_id.phase_ids.sequence', 'project_id.phase_ids.duration_days')
    def _compute_dates(self):
        for phase in self:
            project = phase.project_id
            phases = project.phase_ids.sorted('sequence')
            if not phases:
                continue

            if project.planning_mode == 'forward' and project.date_start:
                current_date = project.date_start
                for p in phases:
                    p.date_start = current_date
                    p.date_end = current_date + timedelta(days=p.duration_days - 1)
                    current_date = p.date_end + timedelta(days=1)

            elif project.planning_mode == 'backward' and project.date_launch:
                current_date = project.date_launch
                for p in reversed(phases):
                    p.date_end = current_date
                    p.date_start = current_date - timedelta(days=p.duration_days - 1)
                    current_date = p.date_start - timedelta(days=1)

    def _compute_progress(self):
        for phase in self:
            today = fields.Date.context_today(self)
            if not phase.date_start or not phase.date_end:
                phase.progress = 0.0
            elif today < phase.date_start:
                phase.progress = 0.0
            elif today > phase.date_end:
                phase.progress = 100.0
            else:
                elapsed = (today - phase.date_start).days
                total = (phase.date_end - phase.date_start).days + 1
                phase.progress = min(100.0, round((elapsed / total) * 100, 1))
