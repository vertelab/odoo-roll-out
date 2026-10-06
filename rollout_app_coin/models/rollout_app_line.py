# -*- coding: utf-8 -*-
# Part of Vertel. See LICENSE file for full copyright and licensing details.

from odoo import _, models


class RolloutAppLine(models.Model):
    """Pay coins into gamification_coin when a line is completed.

    The app is the source; the currency is owned by ``gamification_coin``.
    This bridge only reports the completion.
    """

    _inherit = 'rollout.app.line'

    def _complete(self, source=None):
        """Complete the line, then credit the coins.

        The idempotence guard lives in the base ``_complete``: it returns
        False when the line is already done, so coins cannot be credited
        twice even if this is called again.
        """
        became_done = super()._complete(source=source)
        if not became_done:
            return False

        self._credit_coins()
        return True

    def _credit_coins(self):
        """Credit ``coins_earned`` to the user's coin balance.

        Skipped when the line is worth nothing, so no empty ledger rows are
        created. The ledger entry's ``origin_ref`` points back at this line,
        which is what makes the credit traceable to the task that earned it.
        """
        self.ensure_one()
        coins = self.coins_earned
        if not coins:
            return
        self.user_id._add_coins(
            coins,
            source=self,
            reason=_("Completed: %(line)s", line=self.name),
        )
