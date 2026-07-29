# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class RolloutTask(models.Model):
    _name = 'rollout.task'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Rollout Task'
    _order = 'sequence, id'

    name = fields.Char(required=True, translate=True, tracking=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)

    # ── Parent ──
    phase_id = fields.Many2one(
        'rollout.phase', required=True, ondelete='cascade', string='Phase',
    )
    project_id = fields.Many2one(
        related='phase_id.project_id', store=True, string='Project',
    )

    # ── Role ──
    role_id = fields.Many2one('rollout.role', string='Role')

    # ── Assignment ──
    assigned_to = fields.Many2one('res.users', string='Assigned To', tracking=True)

    # ── Timing ──
    date_deadline = fields.Date(string='Deadline')

    # ── State ──
    state = fields.Selection([
        ('draft', 'Draft'),
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], default='todo', tracking=True)

    # ── Content ──
    description = fields.Html(translate=True, string='Description')
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Medium'),
        ('2', 'High'),
        ('3', 'Urgent'),
    ], default='1')

    def action_start(self):
        self.ensure_one()
        self.state = 'in_progress'

    def action_done(self):
        self.state = 'done'

    def action_cancel(self):
        self.state = 'cancelled'
