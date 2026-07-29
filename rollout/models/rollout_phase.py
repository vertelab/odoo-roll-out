# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date, timedelta

from odoo import _, api, fields, models


class RolloutPhase(models.Model):
    _name = 'rollout.phase'
    _description = 'Rollout Phase (ADKAR)'
    _order = 'sequence, id'

    project_id = fields.Many2one(
        'rollout.project', required=True, ondelete='cascade',
    )
    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    # ── ADKAR ──
    adkar_phase = fields.Selection([
        ('awareness', 'Awareness — Why?'),
        ('desire', 'Desire — Want to?'),
        ('knowledge', 'Knowledge — How to?'),
        ('ability', 'Ability — Can do?'),
        ('reinforcement', 'Reinforcement — Keep doing?'),
    ], required=True)

    # ── Timeline ──
    duration_days = fields.Integer(default=30, required=True)
    date_start = fields.Date(
        compute='_compute_dates', store=True, string='Start Date',
    )
    date_end = fields.Date(
        compute='_compute_dates', store=True, string='End Date',
    )

    # ── Gate ──
    gate_type = fields.Selection([
        ('none', 'No Gate'),
        ('approval', 'Approval Required'),
        ('metric', 'Metric Threshold'),
        ('completion', 'All Tasks Complete'),
    ], default='completion')
    gate_metric = fields.Float(string='Threshold Value')
    gate_passed = fields.Boolean(default=False)

    # ── Relations ──
    task_ids = fields.One2many('rollout.task', 'phase_id', string='Tasks')
    role_ids = fields.Many2many('rollout.role', string='Roles in this Phase')

    # ── Computed ──
    task_count = fields.Integer(compute='_compute_task_count', string='Tasks')
    task_done_count = fields.Integer(compute='_compute_task_count', string='Done')

    @api.depends('task_ids', 'task_ids.state')
    def _compute_task_count(self):
        for p in self:
            tasks = p.task_ids
            p.task_count = len(tasks)
            p.task_done_count = len(tasks.filtered(lambda t: t.state == 'done'))

    @api.depends('project_id.planning_mode', 'project_id.date_start',
                  'project_id.date_launch', 'duration_days', 'sequence')
    def _compute_dates(self):
        """Compute phase dates based on project planning mode."""
        for phase in self:
            project = phase.project_id
            if not project:
                continue

            if project.planning_mode == 'forward':
                self._compute_forward(phase, project)
            else:
                self._compute_backward(phase, project)

    def _compute_forward(self, phase, project):
        """Forward: start from date_start, chain phases sequentially."""
        if not project.date_start:
            return
        phases = project.phase_ids.filtered(
            lambda p: p.sequence < phase.sequence
        ).sorted('sequence')
        if not phases:
            phase.date_start = project.date_start
        else:
            last = phases[-1]
            if last.date_end:
                phase.date_start = last.date_end + timedelta(days=1)
            else:
                return
        phase.date_end = phase.date_start + timedelta(days=phase.duration_days - 1)

    def _compute_backward(self, phase, project):
        """Backward: start from date_launch, chain phases in reverse."""
        if not project.date_launch:
            return
        phases = project.phase_ids.filtered(
            lambda p: p.sequence > phase.sequence
        ).sorted('sequence')
        if not phases:
            phase.date_end = project.date_launch
        else:
            next_phase = phases[0]
            if next_phase.date_start:
                phase.date_end = next_phase.date_start - timedelta(days=1)
            else:
                return
        phase.date_start = phase.date_end - timedelta(days=phase.duration_days - 1)
