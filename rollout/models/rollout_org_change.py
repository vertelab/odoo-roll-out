# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class RolloutOrgChange(models.Model):
    _name = 'rollout.org_change'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Organizational Change (Rollout)'
    _order = 'phase_id, name'

    project_id = fields.Many2one(
        'rollout.project', required=True, ondelete='cascade',
    )
    phase_id = fields.Many2one('rollout.phase', string='Phase')
    name = fields.Char(required=True, tracking=True)
    active = fields.Boolean(default=True)

    # ── Change Type ──
    change_type = fields.Selection([
        ('new_dept', 'New Department'),
        ('restructure', 'Restructure'),
        ('new_role', 'New Role / Position'),
        ('merge', 'Merge'),
        ('split', 'Split'),
        ('reporting', 'New Reporting Line'),
        ('other', 'Other'),
    ], required=True, string='Change Type', tracking=True)

    # ── HR References (added by rollout_hr bridge when hr module is installed) ──
    # department_id, job_ids, employee_ids are added by rollout_hr bridge
    department_name = fields.Char(string='Department Name',
        help='Department name. When hr module is installed, rollout_hr bridge adds department_id field.')

    description = fields.Html(translate=True)

    # ── Status ──
    status = fields.Selection([
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('done', 'Completed'),
    ], default='planned', tracking=True)

    def action_start(self):
        self.status = 'in_progress'

    def action_done(self):
        self.status = 'done'
