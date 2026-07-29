# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class RolloutPhase(models.Model):
    _inherit = 'rollout.phase'

    mgmt_clause_ids = fields.Many2many(
        'mgmtsystem.clause', string='ISO Clauses',
        help='ISO clauses addressed in this phase',
    )
    mgmt_policy_id = fields.Many2one(
        'mgmtsystem.policy', string='Related Policy',
    )
