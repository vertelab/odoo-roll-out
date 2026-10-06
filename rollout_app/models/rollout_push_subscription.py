# -*- coding: utf-8 -*-
# Part of Vertel. See LICENSE file for full copyright and licensing details.

import json
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

try:
    from pywebpush import webpush, WebPushException
except ImportError:
    webpush = None
    WebPushException = None


class RolloutPushSubscription(models.Model):
    """A Web Push subscription, one per device per user.

    A user may subscribe from several devices, so this is a list, not a
    field on res.users. Also carries the dispatch that sends to them.
    """

    _name = 'rollout.push.subscription'
    _description = 'Rollout Push Subscription'
    _order = 'create_date desc'

    user_id = fields.Many2one(
        'res.users', string='User', required=True, ondelete='cascade',
        index=True)
    endpoint = fields.Char('Endpoint', required=True)
    p256dh = fields.Char('P-256 DH Key', required=True)
    auth = fields.Char('Auth Secret', required=True)
    user_agent = fields.Char('Device')

    active = fields.Boolean(
        'Active', default=True,
        help="Set to false when the push service reports the subscription "
             "as gone (HTTP 410). Inactive subscriptions are not sent to.")

    _sql_constraints = [
        ('unique_endpoint', 'UNIQUE(endpoint)',
         'This push endpoint is already subscribed.'),
    ]

    # ------------------------------------------------------------------
    # VAPID configuration
    # ------------------------------------------------------------------
    def _get_vapid_private_key(self):
        return self.env['ir.config_parameter'].sudo().get_param(
            'rollout_app.vapid_private_key')

    def _get_vapid_claims(self):
        """VAPID claims. The subject must be a mailto: or https: URL."""
        subject = self.env['ir.config_parameter'].sudo().get_param(
            'rollout_app.vapid_subject', 'mailto:info@vertel.se')
        return {'sub': subject}

    # ------------------------------------------------------------------
    # Send
    # ------------------------------------------------------------------
    def _send(self, title, body, url=None):
        """Send one push notification to this subscription.

        Returns True on success. On HTTP 404/410 the subscription is
        deactivated — the device is no longer reachable, and retrying would
        only waste time.
        """
        self.ensure_one()
        if webpush is None:
            _logger.warning(
                "rollout_app: pywebpush is not installed; cannot send push.")
            return False

        private_key = self._get_vapid_private_key()
        if not private_key:
            _logger.warning(
                "rollout_app: no VAPID private key configured; skipping push.")
            return False

        payload = json.dumps({
            'title': title,
            'body': body,
            'url': url or '/odoo',
        })

        try:
            webpush(
                subscription_info={
                    'endpoint': self.endpoint,
                    'keys': {'p256dh': self.p256dh, 'auth': self.auth},
                },
                data=payload,
                vapid_private_key=private_key,
                vapid_claims=self._get_vapid_claims(),
            )
            return True
        except WebPushException as exc:
            status = getattr(exc.response, 'status_code', None)
            if status in (404, 410):
                _logger.info(
                    "rollout_app: subscription %s is gone; deactivating.",
                    self.id)
                self.active = False
            else:
                _logger.warning(
                    "rollout_app: push to %s failed (%s).", self.id, exc)
            return False
        except Exception as exc:  # noqa: BLE001 — never break the cron
            _logger.warning("rollout_app: push to %s failed: %s", self.id, exc)
            return False

    @api.model
    def cron_rollout_push_dispatch(self):
        """Send staged push notifications.

        The bus is not durable, so a notification that must survive until a
        cron runs is staged in ``rollout.push.queue`` first. This drains it.
        """
        queue = self.env['rollout.push.queue'].search(
            [('state', '=', 'pending')], limit=200)
        sent = 0
        for item in queue:
            for subscription in item.user_id.push_subscription_ids.filtered(
                    'active'):
                if subscription._send(item.title, item.body, item.url):
                    sent += 1
            item.state = 'sent'
        return sent
