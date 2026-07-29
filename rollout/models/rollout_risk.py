# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class RolloutRisk(models.Model):
    _name = 'rollout.risk'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Rollout Risk'
    _order = 'risk_score desc, id'

    project_id = fields.Many2one(
        'rollout.project', required=True, ondelete='cascade',
    )
    phase_id = fields.Many2one(
        'rollout.phase', string='Phase',
    )
    name = fields.Char(required=True, tracking=True)
    description = fields.Text()

    # ── Scoring ──
    probability = fields.Selection([
        ('1', '1 — Very Low'),
        ('2', '2 — Low'),
        ('3', '3 — Medium'),
        ('4', '4 — High'),
        ('5', '5 — Very High'),
    ], required=True, default='3', tracking=True)
    impact = fields.Selection([
        ('1', '1 — Negligible'),
        ('2', '2 — Minor'),
        ('3', '3 — Moderate'),
        ('4', '4 — Major'),
        ('5', '5 — Critical'),
    ], required=True, default='3', tracking=True)
    risk_score = fields.Integer(compute='_compute_score', store=True)

    # ── Management ──
    mitigation = fields.Text(string='Mitigation Plan')
    trigger_event = fields.Char(string='Trigger Event')
    owner_id = fields.Many2one('res.users', string='Risk Owner', tracking=True)

    # ── State ──
    state = fields.Selection([
        ('identified', 'Identified'),
        ('monitoring', 'Monitoring'),
        ('materialized', 'Materialized'),
        ('mitigated', 'Mitigated'),
    ], default='identified', tracking=True)

    @api.depends('probability', 'impact')
    def _compute_score(self):
        for r in self:
            r.risk_score = int(r.probability) * int(r.impact)
