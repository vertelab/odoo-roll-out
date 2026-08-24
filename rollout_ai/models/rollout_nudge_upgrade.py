"""Nudge Upgrade — enrich rollout.nudge with odoo-mind delivery channels."""

import logging
from datetime import datetime, timedelta

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)

# Anti-spam defaults
MAX_NUDGES_PER_DAY = 3
MIN_INTERVAL_HOURS = 2


class RolloutNudgeUpgrade(models.AbstractModel):
    _name = 'rollout.nudge.upgrade'
    _description = 'Upgrade rollout nudges to odoo-mind channels'

    @api.model
    def _upgrade_nudge_delivery(self, nudge, user, message, context=None):
        """Deliver nudge via odoo-mind channels instead of simple notification.

        Primary: mail.activity (todo with deadline)
        Also checks: calendar triggers, email fallback
        """
        # Check anti-spam
        if not self._check_anti_spam(user):
            _logger.info("rollout_ai: Nudge delayed for %s (anti-spam)", user.name)
            return False

        # Create mail.activity as primary delivery
        deadline = fields.Date.today() + timedelta(days=2)
        activity = self.env['mail.activity'].create({
            'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
            'summary': nudge.name,
            'note': message,
            'user_id': user.id,
            'date_deadline': deadline,
        })

        # Track exposure (will be updated when user opens)
        nudge.write({
            'exposure_count': nudge.exposure_count + 1,
        })

        # Check calendar for relevant events
        self._check_calendar_trigger(user, nudge, message)

        # Check if user needs email fallback
        self._check_email_fallback(user, nudge, message)

        return True

    @api.model
    def _check_anti_spam(self, user):
        """Enforce anti-spam thresholds.

        Returns True if nudge should be delivered.
        """
        today = fields.Date.today()
        recent_activities = self.env['mail.activity'].search_count([
            ('user_id', '=', user.id),
            ('create_date', '>=', today),
        ])
        return recent_activities < MAX_NUDGES_PER_DAY

    @api.model
    def _check_calendar_trigger(self, user, nudge, message):
        """Check for relevant calendar events and deliver timed nudges."""
        now = fields.Datetime.now()
        window_start = now
        window_end = now + timedelta(hours=1)

        events = self.env['calendar.event'].search([
            ('partner_ids.user_ids', 'in', user.id),
            ('start', '>=', window_start.strftime('%Y-%m-%d %H:%M:%S')),
            ('start', '<=', window_end.strftime('%Y-%m-%d %H:%M:%S')),
        ])

        if events:
            for event in events[:1]:
                self.env['bus.bus']._sendone(
                    user.partner_id,
                    'simple_notification',
                    {
                        'title': f'Inför {event.name}: {nudge.name}',
                        'message': message,
                        'sticky': True,
                        'warning': False,
                    }
                )

    @api.model
    def _check_email_fallback(self, user, nudge, message):
        """Send email summary if user hasn't logged in for 3+ days."""
        if not user.login_date:
            return

        last_login = user.login_date
        days_since_login = (fields.Datetime.now() - last_login).days

        if days_since_login >= 3:
            # Queue email via mail.template
            _logger.info(
                "rollout_ai: User %s absent %d days — email fallback",
                user.name, days_since_login)
            # In production: use mail.template to send summary
            self.env['mail.activity'].create({
                'activity_type_id': self.env.ref(
                    'mail.mail_activity_data_email').id,
                'summary': f'Rollout update: {nudge.name}',
                'note': f'Du har varit frånvarande i {days_since_login} dagar.\n\n{message}',
                'user_id': user.id,
            })


class RolloutNudge(models.Model):
    _inherit = 'rollout.nudge'

    def _deliver_enriched(self, user, message, context=None):
        """Override: deliver via odoo-mind channels."""
        upgrader = self.env['rollout.nudge.upgrade']
        return upgrader._upgrade_nudge_delivery(self, user, message, context)

    def action_track_exposure(self, user_id):
        """Called when user views/open the nudge activity."""
        user = self.env['res.users'].browse(user_id)
        self.write({
            'exposure_count': self.exposure_count + 1,
        })

    def action_track_action(self, user_id):
        """Called when user takes action on the nudge."""
        self.write({
            'action_count': self.action_count + 1,
        })

    def action_track_outcome(self, user_id):
        """Called when the desired behavior change is observed."""
        self.write({
            'outcome_count': self.outcome_count + 1,
        })
