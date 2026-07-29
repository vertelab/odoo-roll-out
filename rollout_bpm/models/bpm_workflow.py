# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class BPMWorkflow(models.Model):
    _inherit = 'bpm.workflow'

    rollout_project_id = fields.Many2one(
        'rollout.project', string='Rollout Project',
        help='Rollout project this process belongs to',
    )
