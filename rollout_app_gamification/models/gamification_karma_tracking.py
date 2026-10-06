# -*- coding: utf-8 -*-
# Part of Vertel. See LICENSE file for full copyright and licensing details.

from odoo import _, models


class KarmaTracking(models.Model):
    """Allow a rollout app line to be the source of a karma change.

    ``gamification.karma.tracking.origin_ref`` validates its value against a
    selection. Out of the box that selection only contains ``res.users``, so
    crediting karma with a ``rollout.app.line`` as the source raises::

        ValueError: Wrong value for gamification.karma.tracking.origin_ref:
        'rollout.app.line,28'

    Odoo's own bridges extend the selection rather than bypassing it
    (``website_slides`` adds ``slide.slide`` and ``slide.channel``), so this
    follows the same pattern.
    """

    _inherit = 'gamification.karma.tracking'

    def _get_origin_selection_values(self):
        return super()._get_origin_selection_values() + [
            ('rollout.app.line', _('Rollout App Line')),
        ]
