# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class RolloutNudge(models.Model):
    _name = 'rollout.nudge'
    _description = 'Rollout Behavioral Nudge'
    _order = 'sequence, id'

    project_id = fields.Many2one(
        'rollout.project', required=True, ondelete='cascade',
    )
    phase_id = fields.Many2one('rollout.phase', string='Phase Scope')
    role_id = fields.Many2one('rollout.role', string='Role Scope')
    name = fields.Char(required=True, string='Nudge Name')
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    # ── Trigger ──
    trigger_event = fields.Selection([
        ('course_completed', 'Course Completed'),
        ('login_streak', 'Login Streak Milestone'),
        ('phase_transition', 'Phase Transition'),
        ('badge_awarded', 'Badge Awarded'),
        ('competency_milestone', 'Competency Milestone'),
        ('sentiment_drop', 'Sentiment Drop'),
        ('custom', 'Custom'),
    ], required=True, string='Trigger Event')

    # ── Nudge Type ──
    nudge_type = fields.Selection([
        ('social_proof', 'Social Proof'),
        ('loss_aversion', 'Loss Aversion'),
        ('default_nudge', 'Default Effect'),
        ('framing', 'Positive Framing'),
        ('commitment', 'Commitment/Consistency'),
    ], required=True, string='Nudge Type')

    # ── Message ──
    template = fields.Text(
        required=True, string='Message Template',
        help='Use placeholders: {user}, {role}, {phase}, {course_name}, '
             '{badge_name}, {streak_days}, {team_progress}',
    )

    def render_template(self, **context):
        """Render the nudge template with provided context."""
        self.ensure_one()
        try:
            return self.template.format(**context)
        except (KeyError, ValueError):
            return self.template
