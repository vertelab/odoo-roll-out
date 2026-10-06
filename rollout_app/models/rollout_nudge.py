# -*- coding: utf-8 -*-
# Part of Vertel. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class RolloutNudge(models.Model):
    """Extend the nudge engine with the app's weekly rhythm.

    No new trigger engine: the three new events reuse the existing
    ``trigger_event`` field, so exposure/action/outcome measurement applies
    to them without a separate path.
    """

    _inherit = 'rollout.nudge'

    trigger_event = fields.Selection(
        selection_add=[
            ('period_published', 'Period Published'),
            ('still_open', 'Line Still Open'),
            ('line_completed', 'Line Completed'),
        ],
        # 'cascade' removes nudges carrying these values when this module is
        # uninstalled. 'set null' is invalid here: the field is required.
        ondelete={
            'period_published': 'cascade',
            'still_open': 'cascade',
            'line_completed': 'cascade',
        },
    )
