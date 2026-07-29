# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class RolloutSentiment(models.Model):
    _name = 'rollout.sentiment'
    _description = 'Rollout Sentiment Entry'
    _order = 'create_date desc'
    _rec_name = 'user_id'

    project_id = fields.Many2one(
        'rollout.project', required=True, ondelete='cascade',
    )
    phase_id = fields.Many2one('rollout.phase', string='Phase')
    user_id = fields.Many2one(
        'res.users', required=True, string='User',
        default=lambda self: self.env.user,
    )

    # ── Score ──
    score = fields.Integer(
        required=True, string='Sentiment (1-5)',
        help='1 = Very negative, 5 = Very positive',
    )

    # ── Text ──
    free_text = fields.Text(string='Comment')

    # ── AI Analysis ──
    ai_hotspot = fields.Boolean(
        string='Flagged as Hotspot',
        help='AI analysis flagged this as a potential concern',
    )
    ai_category = fields.Char(string='AI Category')

    # ── Computed aggregation helpers ──
    create_date = fields.Datetime(string='Submitted', default=fields.Datetime.now)
