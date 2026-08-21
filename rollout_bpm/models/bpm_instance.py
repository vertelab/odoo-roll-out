# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class BPMInstance(models.Model):
    _inherit = "bpm.instance"

    rollout_project_id = fields.Many2one(
        "rollout.project", string="Rollout Project",
        help="Rollout project this process instance belongs to",
        index=True,
    )
