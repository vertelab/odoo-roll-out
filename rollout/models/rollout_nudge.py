"""Rollout Nudge — behavioral nudging engine for rollout projects.

Standalone — no AI dependency. Uses template + trigger + role/phase scope.
When `rollout_ai` is installed, `enriched_by_ai` enables odoo-mind delivery.
"""

from odoo import models, fields, api, _
from string import Formatter


class RolloutNudge(models.Model):
    _name = 'rollout.nudge'
    _description = 'Rollout Nudge'
    _order = 'sequence, id'

    project_id = fields.Many2one(
        'rollout.project', string='Project', required=True, ondelete='cascade')
    phase_id = fields.Many2one(
        'rollout.phase', string='Phase', ondelete='set null')
    role_id = fields.Many2one(
        'rollout.role', string='Target Role', ondelete='set null')

    name = fields.Char('Nudge Name', required=True)
    sequence = fields.Integer('Sequence', default=10)
    active = fields.Boolean('Active', default=True)

    # -- Trigger --
    trigger_event = fields.Selection([
        ('course_completed', 'Course Completed'),
        ('login_streak', 'Login Streak'),
        ('phase_transition', 'Phase Transition'),
        ('badge_awarded', 'Badge Awarded'),
        ('competency_milestone', 'Competency Milestone'),
        ('custom', 'Custom'),
    ], required=True, string='Trigger Event')

    # -- Nudge type (behavioral science) --
    nudge_type = fields.Selection([
        ('social_proof', 'Social Proof'),
        ('loss_aversion', 'Loss Aversion'),
        ('default_effect', 'Default Effect'),
        ('friction_reduction', 'Friction Reduction'),
        ('salience', 'Salience'),
        ('implementation_intention', 'Implementation Intention'),
        ('custom', 'Custom'),
    ], default='social_proof', string='Nudge Type')

    # -- Template --
    template = fields.Text('Message Template', required=True)
    # Supported placeholders: {user}, {role}, {phase}, {course_name},
    # {badge_name}, {streak_days}, {team_progress}

    # -- Delivery --
    enriched_by_ai = fields.Boolean(
        'Enriched by AI',
        help='When True, delivery is handled by odoo-mind channels '
             '(mail.activity, calendar triggers, email) with 3-level measurement')

    # -- Measurement (populated when enriched_by_ai) --
    exposure_count = fields.Integer('Exposure Count')
    action_count = fields.Integer('Action Count')
    outcome_count = fields.Integer('Outcome Count')

    def render_template(self, context):
        """Render the nudge template with the given context dict."""
        try:
            return self.template.format(**context)
        except (KeyError, ValueError) as e:
            return self.template  # Return unrendered if placeholders missing

    def validate_template(self):
        """Validate that all placeholders are recognized."""
        valid_placeholders = {
            '{user}', '{role}', '{phase}', '{course_name}',
            '{badge_name}', '{streak_days}', '{team_progress}',
        }
        try:
            placeholders = {
                f'{{{fn}}}' for _, fn, _, _ in Formatter().parse(self.template)
                if fn is not None
            }
            unknown = placeholders - valid_placeholders
            if unknown:
                return False, f'Unknown placeholders: {", ".join(unknown)}'
            return True, 'OK'
        except ValueError as e:
            return False, str(e)

    def trigger(self, event, user, context=None):
        """Evaluate and deliver this nudge if applicable."""
        if context is None:
            context = {}
        if self.trigger_event != event:
            return False
        if not self.active:
            return False

        # Phase scope check
        if (self.phase_id
                and self.project_id.phase_ids
                and self.phase_id != self.project_id.phase_ids[0]):
            return False

        message = self.render_template(context)
        if self.enriched_by_ai:
            # Delegate to odoo-mind (requires rollout_ai)
            return self._deliver_enriched(user, message, context)
        else:
            # Simple Odoo notification
            return self._deliver_simple(user, message)

    def _deliver_simple(self, user, message):
        """Deliver nudge as a simple Odoo notification."""
        self.env['bus.bus']._sendone(
            user.partner_id,
            'simple_notification',
            {
                'title': self.name,
                'message': message,
                'sticky': False,
                'warning': False,
            }
        )
        return True

    def _deliver_enriched(self, user, message, context):
        """Placeholder — overridden by rollout_ai bridge when installed."""
        # Fall back to simple delivery if AI not available
        return self._deliver_simple(user, message)

    _sql_constraints = [
        ('check_template_not_empty',
         'CHECK(char_length(template) > 0)',
         'Nudge template cannot be empty'),
    ]
