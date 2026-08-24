"""Extend rollout.nudge with internal delivery channels."""

from odoo import models, api


class RolloutNudge(models.Model):
    _inherit = 'rollout.nudge'

    def _deliver_simple(self, user, message):
        """Deliver nudge via Odoo notification in internal context."""
        self.env['bus.bus']._sendone(
            user.partner_id,
            'simple_notification',
            {
                'title': self.name,
                'message': message,
                'sticky': True,
                'warning': False,
            }
        )
        # Also create an activity for tracking
        self.env['mail.activity'].create({
            'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
            'summary': self.name,
            'note': message,
            'user_id': user.id,
            'date_deadline': fields.Date.today(),
        })
        return True
