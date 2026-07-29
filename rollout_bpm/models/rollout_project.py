# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class RolloutProject(models.Model):
    _inherit = 'rollout.project'

    bpm_workflow_id = fields.Many2one(
        'bpm.workflow', string='BPM Process',
        help='BPMN process definition for this rollout',
    )
    bpm_instance_ids = fields.One2many(
        'bpm.instance', 'rollout_project_id', string='Process Instances',
    )
