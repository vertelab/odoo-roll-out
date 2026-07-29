# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SlideChannel(models.Model):
    _inherit = 'slide.channel'

    rollout_role_id = fields.Many2one(
        'rollout.role', string='Rollout Role',
        help='Rollout role this course is required for',
    )
