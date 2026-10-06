# -*- coding: utf-8 -*-
# Part of Vertel. See LICENSE file for full copyright and licensing details.

from datetime import timedelta

from odoo import api, fields, models


class RolloutNudge(models.Model):
    """Add push as a delivery channel, with in-app fallback.

    Push is additive, not a replacement: the in-app notification is always
    sent, and a push is staged for every active subscription. That is the
    fallback — a user who never granted permission, or who has no
    subscription, still sees the nudge in Odoo.
    """

    _inherit = 'rollout.nudge'

    push_sent_count = fields.Integer(
        'Push Notifications Sent', default=0, readonly=True)

    def _deliver_simple(self, user, message):
        """Deliver in-app, and stage a push if the user has a subscription."""
        result = super()._deliver_simple(user, message)
        self._stage_push(user, message)
        return result

    def _stage_push(self, user, message):
        """Stage a push notification for the dispatch cron.

        Respects the daily maximum across all channels: if the user has
        already received their allowance today, no push is staged. This is
        what keeps the cap channel-independent.
        """
        self.ensure_one()
        if not self._push_allowed(user):
            return False

        self.env['rollout.push.queue'].sudo().create({
            'user_id': user.id,
            'title': self.name,
            'body': message,
            'url': '/odoo',
            'nudge_id': self.id,
        })
        self.sudo().push_sent_count += 1
        return True

    @api.model
    def _push_allowed(self, user):
        """Whether this user may receive another push today.

        The daily maximum is read from a config parameter so it can be tuned
        without a code change, and it counts nudges staged across *all*
        channels — a push is not exempt just because it is a different
        medium.
        """
        maximum = int(self.env['ir.config_parameter'].sudo().get_param(
            'rollout_app.push_daily_max', 3))
        if maximum <= 0:
            return True
        since = fields.Datetime.now() - timedelta(days=1)
        staged = self.env['rollout.push.queue'].sudo().search_count([
            ('user_id', '=', user.id),
            ('create_date', '>=', since),
        ])
        return staged < maximum
