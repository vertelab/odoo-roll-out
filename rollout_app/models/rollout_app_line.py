# -*- coding: utf-8 -*-
# Part of Vertel. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class RolloutAppLine(models.Model):
    """One person's outcome for one module line.

    This is what makes the menu personal: status, points and source per
    person. "Greyed out", team totals and the weekly summary are all
    projections of this row.
    """

    _name = 'rollout.app.line'
    _description = 'Rollout App Participant Line'
    _order = 'period_start desc, id desc'

    app_id = fields.Many2one(
        'rollout.app', string='App', required=True, ondelete='cascade',
        index=True)
    module_line_id = fields.Many2one(
        'rollout.module.line', string='Line', required=True,
        ondelete='cascade', index=True)
    user_id = fields.Many2one(
        'res.users', string='User', required=True, ondelete='cascade',
        index=True)

    state = fields.Selection([
        ('open', 'Open'),
        ('done', 'Done'),
    ], string='Status', default='open', required=True, index=True,
        help="Only two states. 'Missed' is not a state — it is the query "
             "open AND period_end < now().")

    locked = fields.Boolean(
        'Locked', default=False,
        help="Achievement-gated content, unlocked per person.")

    done_at = fields.Datetime('Completed On', readonly=True)
    points_earned = fields.Integer('Points Earned', readonly=True)
    coins_earned = fields.Integer('Coins Earned', readonly=True)

    source_ref = fields.Reference(
        selection='_selection_source_ref', string='Source',
        help="The record that satisfied the line, e.g. a course completion "
             "or a survey submission. Empty for self-reported lines.")

    # -- Period, copied from the line for queryability --
    period_start = fields.Date('Period Start', related='module_line_id.period_start', store=True)
    period_end = fields.Date('Period End', related='module_line_id.period_end', store=True)
    publish_at = fields.Datetime('Publish At', related='module_line_id.publish_at', store=True)
    remind_at = fields.Datetime('Remind At', related='module_line_id.remind_at', store=True)

    # Denormalised for the view, so the menu does not need a join per row.
    name = fields.Char('Name', related='module_line_id.name')
    points = fields.Integer('Points', related='module_line_id.points')
    coins = fields.Integer('Coins', related='module_line_id.coins')
    badge_id = fields.Many2one('gamification.badge', related='module_line_id.badge_id')
    module_id = fields.Many2one('rollout.module', related='module_line_id.module_id', store=True)

    _sql_constraints = [
        ('one_line_per_person', 'UNIQUE(app_id, module_line_id, user_id)',
         'A person can only have one line per module line.'),
        ('points_non_negative', 'CHECK(points_earned >= 0)',
         'Earned points cannot be negative.'),
        ('coins_non_negative', 'CHECK(coins_earned >= 0)',
         'Earned coins cannot be negative.'),
    ]

    @api.model
    def _selection_source_ref(self):
        """Models that may satisfy a line. Open — the type gates it."""
        return [
            (model.model, model.name)
            for model in self.env['ir.model'].sudo().search([])
        ]

    # ------------------------------------------------------------------
    # Completion
    # ------------------------------------------------------------------
    def action_mark_done(self):
        """Mark the line done by hand, for self-reported lines."""
        for line in self:
            if line.locked:
                raise UserError(_("This line is locked."))
            line._complete(source=None)
        return True

    def _complete(self, source=None):
        """Complete the line, awarding points exactly once.

        Idempotent: a line already done is left alone, so a re-run (or a
        double trigger) cannot award points twice.
        """
        self.ensure_one()
        if self.state == 'done':
            return False
        if self.locked:
            return False

        self.write({
            'state': 'done',
            'done_at': fields.Datetime.now(),
            'points_earned': self.module_line_id.points,
            'coins_earned': self.module_line_id.coins,
            'source_ref': source,
        })

        # Announce the completion, and unlock anything gated on it.
        self._fire_nudge('line_completed', self.user_id, {
            'line': self.name,
            'points': self.module_line_id.points,
        })
        self._unlock_dependents()
        return True

    def _unlock_dependents(self):
        """Unlock lines gated on this line, for this person only."""
        self.ensure_one()
        dependents = self.env['rollout.module.line'].search([
            ('source_line_id', '=', self.module_line_id.id),
        ])
        if not dependents:
            return
        gated = self.search([
            ('user_id', '=', self.user_id.id),
            ('module_line_id', 'in', dependents.ids),
            ('locked', '=', True),
        ])
        for line in gated:
            line.action_unlock()
            line._fire_nudge('line_completed', self.user_id, {
                'line': line.name,
                'unlocked': True,
            })

    def action_unlock(self):
        """Unlock an achievement-gated line for this person."""
        for line in self:
            if line.locked:
                line.locked = False
        return True

    # ------------------------------------------------------------------
    # Visibility
    # ------------------------------------------------------------------
    @api.model
    def _visible_domain(self, user=None):
        """Lines visible in the personal view right now.

        Published and not past their period. A line whose period has ended
        leaves the view but stays in data, so the weekly summary can still
        report on it.
        """
        user = user or self.env.user
        now = fields.Datetime.now()
        today = fields.Date.today()
        return [
            ('user_id', '=', user.id),
            '|', ('publish_at', '=', False), ('publish_at', '<=', now),
            '|', ('period_end', '=', False), ('period_end', '>=', today),
        ]

    @api.model
    def _missed_domain(self, user=None):
        """Open lines whose period has ended — the query that replaces a
        'missed' state."""
        user = user or self.env.user
        return [
            ('user_id', '=', user.id),
            ('state', '=', 'open'),
            ('period_end', '!=', False),
            ('period_end', '<', fields.Date.today()),
        ]

    def _is_missed(self):
        self.ensure_one()
        return (
            self.state == 'open'
            and self.period_end
            and self.period_end < fields.Date.today()
        )

    # ------------------------------------------------------------------
    # Reminders
    # ------------------------------------------------------------------
    @api.model
    def cron_rollout_app_remind(self):
        """Evaluate 'still_open' reminders for lines past their remind_at.

        Social proof: the nudge can state how many colleagues have already
        acted, which is what makes the reminder persuasive rather than
        nagging.
        """
        now = fields.Datetime.now()
        due = self.search([
            ('state', '=', 'open'),
            ('remind_at', '!=', False),
            ('remind_at', '<=', now),
            '|', ('period_end', '=', False),
                 ('period_end', '>=', fields.Date.today()),
        ])

        sent = 0
        for line in due:
            app = line.app_id
            # How many of the team have already completed this line?
            total = len(app.project_id.team_member_ids)
            done = self.search_count([
                ('app_id', '=', app.id),
                ('module_line_id', '=', line.module_line_id.id),
                ('state', '=', 'done'),
            ])
            self._fire_nudge('still_open', line.user_id, {
                'line': line.name,
                'team_progress': f'{done} av {total}',
            })
            sent += 1
        return sent

    def _fire_nudge(self, event, user, context):
        """Fire every active nudge matching this event, for this user."""
        nudges = self.env['rollout.nudge'].search([
            ('trigger_event', '=', event),
            ('active', '=', True),
        ])
        for nudge in nudges:
            nudge.trigger(event, user, context)
    # ------------------------------------------------------------------
    @api.model
    def cron_rollout_app_autoclear(self):
        """Complete lines whose source record now exists.

        For a course line, a matching ``slide.channel.partner`` means the
        course is done. For a survey line, a completed
        ``survey.user_input``. This is what lets a line clear without the
        person confirming anything.
        """
        cleared = 0
        open_lines = self.search([
            ('state', '=', 'open'),
            ('module_line_id.module_rel', '!=', False),
        ])
        for line in open_lines:
            source = line._find_source_record()
            if source and line._complete(source=source):
                cleared += 1
        return cleared

    def _find_source_record(self):
        """Find the record that satisfies this line, if any.

        Returns None when the line has no backing record, or the backing
        model is not one we know how to read.
        """
        self.ensure_one()
        rel = self.module_line_id.module_rel
        if not rel:
            return None
        model = rel._name
        user = self.user_id

        if model == 'slide.channel':
            # A course completion is a slide.channel.partner row whose
            # member_status is 'completed' (website_slides sets it when the
            # last slide is done).
            partner = self.env['slide.channel.partner'].search([
                ('channel_id', '=', rel.id),
                ('partner_id', '=', user.partner_id.id),
                ('member_status', '=', 'completed'),
            ], limit=1)
            return partner or None

        if model == 'survey.survey':
            user_input = self.env['survey.user_input'].search([
                ('survey_id', '=', rel.id),
                ('partner_id', '=', user.partner_id.id),
                ('state', '=', 'done'),
            ], limit=1)
            return user_input or None

        return None
