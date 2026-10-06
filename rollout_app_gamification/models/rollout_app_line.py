# -*- coding: utf-8 -*-
# Part of Vertel. See LICENSE file for full copyright and licensing details.

from odoo import _, models


class RolloutAppLine(models.Model):
    """Report completions to gamification.

    The app is a consumer: gamification owns karma and badges. This bridge
    reports a completion, and unlocks anything gated on it. It never creates
    a badge.
    """

    _inherit = 'rollout.app.line'

    def _complete(self, source=None):
        """Complete the line, then report to gamification.

        The idempotence guard lives in the base ``_complete``: it returns
        False when the line is already done, so karma cannot be awarded
        twice even if this is called again.
        """
        became_done = super()._complete(source=source)
        if not became_done:
            return False

        self._award_karma()
        self._unlock_by_badge()
        return True

    def _award_karma(self):
        """Award karma for the points this line earned.

        Uses ``points_earned``, which the base completion just set from the
        module line. Awarded once, because ``_complete`` only returns True
        on the transition into ``done``.
        """
        self.ensure_one()
        points = self.points_earned
        if not points:
            return
        self.user_id._add_karma(
            points,
            source=self,
            reason=_("Completed: %(line)s", line=self.name),
        )

    def _unlock_by_badge(self):
        """Unlock lines gated on a badge this person now holds.

        A line may be gated on ``unlock_badge_id``. When the person is
        awarded that badge, their locked line opens. Per person: only this
        user's line is unlocked.
        """
        self.ensure_one()
        user = self.user_id
        badge_ids = user.badge_ids.mapped('badge_id').ids
        if not badge_ids:
            return

        gated = self.search([
            ('user_id', '=', user.id),
            ('locked', '=', True),
            ('module_line_id.unlock_badge_id', 'in', badge_ids),
        ])
        for line in gated:
            line.action_unlock()
