# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class RolloutProject(models.Model):
    _inherit = 'rollout.project'

    mgmtsystem_id = fields.Many2one(
        'mgmtsystem.system', string='Management System',
        help='Linked ISO management system',
    )
