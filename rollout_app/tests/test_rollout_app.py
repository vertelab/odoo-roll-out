# -*- coding: utf-8 -*-
# Part of Vertel. See LICENSE file for full copyright and licensing details.

from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRolloutApp(TransactionCase):
    """Module types, lines, the app menu and participant outcomes."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.Module = cls.env['rollout.module']
        cls.Line = cls.env['rollout.module.line']
        cls.App = cls.env['rollout.app']
        cls.AppLine = cls.env['rollout.app.line']

        cls.user_a = cls.env['res.users'].create({
            'name': 'Participant A', 'login': 'rollout_participant_a'})
        cls.user_b = cls.env['res.users'].create({
            'name': 'Participant B', 'login': 'rollout_participant_b'})
        cls.outsider = cls.env['res.users'].create({
            'name': 'Outsider', 'login': 'rollout_outsider'})

        cls.project = cls.env['rollout.project'].create({
            'name': 'Test Rollout',
            'customer_id': cls.env['res.partner'].create(
                {'name': 'Test Customer', 'is_company': True}).id,
            'state': 'active',
            'team_member_ids': [(6, 0, [cls.user_a.id, cls.user_b.id])],
        })
        cls.app = cls.App.create({
            'name': 'Test App',
            'project_id': cls.project.id,
        })

    def _make_module(self, **kwargs):
        values = {
            'name': 'Kurs',
            'spawn_mode': 'static',
            'allowed_model': 'slide.channel',
            'default_points': 10,
            'default_coins': 5,
        }
        values.update(kwargs)
        return self.Module.create(values)

    def _make_line(self, module, **kwargs):
        values = {'name': 'CRM kap 3', 'module_id': module.id}
        values.update(kwargs)
        return self.Line.create(values)

    # ------------------------------------------------------------------
    # 1.2 Module types
    # ------------------------------------------------------------------
    def test_create_module_type(self):
        """A module type can be created and its selections validate."""
        module = self._make_module()
        self.assertEqual(module.spawn_mode, 'static')
        self.assertEqual(module.recurrence, 'none')
        self.assertEqual(module.default_points, 10)

    def test_periodic_requires_recurrence(self):
        """A periodic type without a recurrence is refused."""
        with self.assertRaises(ValidationError):
            self._make_module(
                name='Enkät', spawn_mode='periodic', recurrence='none')

    def test_unknown_allowed_model_refused(self):
        """An unknown allowed_model is tolerated (its module may not be
        installed yet), but a line referencing it is still gated."""
        module = self._make_module(allowed_model='does.not.exist')
        self.assertEqual(module.allowed_model, 'does.not.exist')

    # ------------------------------------------------------------------
    # 1.3 / 1.4 Module lines
    # ------------------------------------------------------------------
    def test_create_line_inherits_defaults(self):
        """A line inherits points and coins from its type."""
        module = self._make_module()
        line = self._make_line(module)
        self.assertEqual(line.points, 10)
        self.assertEqual(line.coins, 5)

    def test_module_rel_validated_against_allowed_model(self):
        """A course line cannot reference a survey."""
        module = self._make_module(allowed_model='slide.channel')
        survey = self.env['survey.survey'].create({'title': 'A survey'})
        with self.assertRaises(ValidationError):
            self._make_line(module, module_rel=f'survey.survey,{survey.id}')

    def test_module_rel_allows_matching_model(self):
        """A course line may reference a course."""
        module = self._make_module(allowed_model='slide.channel')
        channel = self.env['slide.channel'].create({'name': 'A course'})
        line = self._make_line(module, module_rel=f'slide.channel,{channel.id}')
        self.assertEqual(line.module_rel, channel)

    def test_empty_allowed_model_permits_anything(self):
        """A type without allowed_model accepts any reference."""
        module = self._make_module(name='Manuell', allowed_model=False)
        survey = self.env['survey.survey'].create({'title': 'S'})
        line = self._make_line(
            module, module_rel=f'survey.survey,{survey.id}')
        self.assertEqual(line.module_rel, survey)

    def test_period_must_be_coherent(self):
        """A period cannot end before it starts."""
        module = self._make_module(
            name='Enkät', spawn_mode='periodic', recurrence='weekly')
        with self.assertRaises(ValidationError):
            self._make_line(
                module, period_start='2026-10-11', period_end='2026-10-05')

    # ------------------------------------------------------------------
    # 1.5 The app
    # ------------------------------------------------------------------
    def test_one_app_per_project(self):
        """A second app for the same project is refused."""
        with self.assertRaises(Exception):
            self.App.create({
                'name': 'Duplicate', 'project_id': self.project.id})

    # ------------------------------------------------------------------
    # 1.6 Participant lines
    # ------------------------------------------------------------------
    def test_app_line_unique_per_person(self):
        """A person cannot have two lines for the same module line."""
        module = self._make_module()
        line = self._make_line(module)
        self.AppLine.create({
            'app_id': self.app.id,
            'module_line_id': line.id,
            'user_id': self.user_a.id,
        })
        with self.assertRaises(Exception):
            self.AppLine.create({
                'app_id': self.app.id,
                'module_line_id': line.id,
                'user_id': self.user_a.id,
            })

    # ------------------------------------------------------------------
    # 2.1 Generation
    # ------------------------------------------------------------------
    def test_generation_for_static_line(self):
        """Creating a static line generates one row per team member."""
        module = self._make_module()
        self.app.module_ids = [(6, 0, [module.id])]
        line = self._make_line(module)
        lines = self.AppLine.search([
            ('module_line_id', '=', line.id),
            ('app_id', '=', self.app.id),
        ])
        self.assertEqual(len(lines), 2)
        self.assertEqual(
            set(lines.mapped('user_id')), {self.user_a, self.user_b})

    def test_generation_is_idempotent(self):
        """Re-running generation creates no duplicates."""
        module = self._make_module()
        self.app.module_ids = [(6, 0, [module.id])]
        line = self._make_line(module)
        before = self.AppLine.search_count([])
        self.Line._generate_app_lines(line)
        self.assertEqual(self.AppLine.search_count([]), before)

    # ------------------------------------------------------------------
    # 2.5 / 2.6 / 2.7 Completion
    # ------------------------------------------------------------------
    def test_manual_completion_awards_points(self):
        """Marking a line done awards points and sets done_at."""
        module = self._make_module()
        self.app.module_ids = [(6, 0, [module.id])]
        line = self._make_line(module)
        app_line = self.AppLine.search([
            ('module_line_id', '=', line.id),
            ('user_id', '=', self.user_a.id)], limit=1)
        app_line.action_mark_done()
        self.assertEqual(app_line.state, 'done')
        self.assertEqual(app_line.points_earned, 10)
        self.assertEqual(app_line.coins_earned, 5)
        self.assertTrue(app_line.done_at)

    def test_points_awarded_only_once(self):
        """A second completion does not award points again."""
        module = self._make_module()
        self.app.module_ids = [(6, 0, [module.id])]
        line = self._make_line(module)
        app_line = self.AppLine.search([
            ('module_line_id', '=', line.id),
            ('user_id', '=', self.user_a.id)], limit=1)
        app_line.action_mark_done()
        app_line.action_mark_done()
        self.assertEqual(app_line.points_earned, 10)

    def test_locked_line_cannot_be_completed(self):
        """A locked line refuses manual completion."""
        module = self._make_module()
        self.app.module_ids = [(6, 0, [module.id])]
        line = self._make_line(module, state='locked')
        app_line = self.AppLine.search([
            ('module_line_id', '=', line.id),
            ('user_id', '=', self.user_a.id)], limit=1)
        self.assertTrue(app_line.locked)
        with self.assertRaises(UserError):
            app_line.action_mark_done()

    # ------------------------------------------------------------------
    # 1.7 Aggregation
    # ------------------------------------------------------------------
    def test_personal_totals(self):
        """A person's totals sum their completed lines."""
        module = self._make_module()
        self.app.module_ids = [(6, 0, [module.id])]
        for i in range(3):
            line = self._make_line(module, name=f'Line {i}')
            app_line = self.AppLine.search([
                ('module_line_id', '=', line.id),
                ('user_id', '=', self.user_a.id)], limit=1)
            app_line.action_mark_done()
        totals = self.app._get_personal_totals(self.user_a)
        self.assertEqual(totals['points'], 30)
        self.assertEqual(totals['coins'], 15)
        self.assertEqual(totals['done'], 3)

    def test_team_total_and_members(self):
        """The team total and per-member breakdown are correct."""
        module = self._make_module()
        self.app.module_ids = [(6, 0, [module.id])]
        line = self._make_line(module)
        for user in (self.user_a, self.user_b):
            app_line = self.AppLine.search([
                ('module_line_id', '=', line.id),
                ('user_id', '=', user.id)], limit=1)
            app_line.action_mark_done()
        self.assertEqual(self.app._get_team_total(), 20)
        member_totals = self.app._get_team_member_totals()
        self.assertEqual(len(member_totals), 2)

    # ------------------------------------------------------------------
    # 2.4 Visibility
    # ------------------------------------------------------------------
    def test_past_period_hidden_but_retained(self):
        """A line past its period leaves the view but stays in data."""
        module = self._make_module(
            name='Enkät', spawn_mode='periodic', recurrence='weekly')
        self.app.module_ids = [(6, 0, [module.id])]
        line = self._make_line(
            module, name='Old survey',
            period_start='2020-01-06', period_end='2020-01-12')
        # A periodic line is not auto-generated; create the participant row.
        app_line = self.AppLine.create({
            'app_id': self.app.id,
            'module_line_id': line.id,
            'user_id': self.user_a.id,
        })

        visible = self.AppLine.search(
            self.AppLine._visible_domain(self.user_a))
        self.assertNotIn(app_line, visible)
        # Still in data, and queryable as missed.
        self.assertTrue(app_line.exists())
        missed = self.AppLine.search(self.AppLine._missed_domain(self.user_a))
        self.assertIn(app_line, missed)

    def test_future_publish_hidden(self):
        """A line not yet published is hidden."""
        module = self._make_module()
        self.app.module_ids = [(6, 0, [module.id])]
        line = self._make_line(
            module, name='Future', publish_at='2099-01-01 07:00:00')
        app_line = self.AppLine.search([
            ('module_line_id', '=', line.id),
            ('user_id', '=', self.user_a.id)], limit=1)
        visible = self.AppLine.search(
            self.AppLine._visible_domain(self.user_a))
        self.assertNotIn(app_line, visible)

    # ------------------------------------------------------------------
    # 3.8 Access control
    # ------------------------------------------------------------------
    def test_outsider_sees_nothing(self):
        """A non-participant has no lines."""
        module = self._make_module()
        self.app.module_ids = [(6, 0, [module.id])]
        self._make_line(module)
        visible = self.AppLine.with_user(self.outsider).search(
            self.AppLine._visible_domain(self.outsider))
        self.assertFalse(visible)

    # ------------------------------------------------------------------
    # 2.3 Spawn cron
    # ------------------------------------------------------------------
    def test_spawn_cron_creates_period_line(self):
        """The spawn cron creates the next period's line."""
        module = self._make_module(
            name='Vecko-enkät', spawn_mode='periodic', recurrence='weekly',
            lead_time=1)
        self.app.module_ids = [(6, 0, [module.id])]
        spawned = self.Line.cron_rollout_app_spawn()
        self.assertTrue(spawned)
        self.assertTrue(spawned.period_start)
        self.assertEqual(spawned.period_end - spawned.period_start, __import__('datetime').timedelta(days=6))
        self.assertTrue(spawned.publish_at)
        self.assertTrue(spawned.remind_at)

    def test_spawn_cron_is_idempotent(self):
        """A second spawn run in the same period creates nothing."""
        module = self._make_module(
            name='Vecko-enkät', spawn_mode='periodic', recurrence='weekly')
        self.app.module_ids = [(6, 0, [module.id])]
        first = self.Line.cron_rollout_app_spawn()
        count = self.Line.search_count([('module_id', '=', module.id)])
        second = self.Line.cron_rollout_app_spawn()
        self.assertEqual(
            self.Line.search_count([('module_id', '=', module.id)]), count)


@tagged('post_install', '-at_install')
class TestRolloutPush(TransactionCase):
    """Push queueing, anti-spam, and dead-subscription handling."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = cls.env['res.users'].create({
            'name': 'Push User', 'login': 'push_user'})
        cls.Sub = cls.env['rollout.push.subscription']
        cls.Queue = cls.env['rollout.push.queue']

    def test_multiple_devices_per_user(self):
        """A user can hold several subscriptions."""
        self.Sub.create({
            'user_id': self.user.id, 'endpoint': 'https://push/one',
            'p256dh': 'k1', 'auth': 'a1', 'user_agent': 'phone'})
        self.Sub.create({
            'user_id': self.user.id, 'endpoint': 'https://push/two',
            'p256dh': 'k2', 'auth': 'a2', 'user_agent': 'tablet'})
        self.assertEqual(
            len(self.user.push_subscription_ids.filtered('active')), 2)

    def test_endpoint_is_unique(self):
        """The same endpoint cannot be subscribed twice."""
        self.Sub.create({
            'user_id': self.user.id, 'endpoint': 'https://push/same',
            'p256dh': 'k', 'auth': 'a'})
        with self.assertRaises(Exception):
            self.Sub.create({
                'user_id': self.user.id, 'endpoint': 'https://push/same',
                'p256dh': 'k', 'auth': 'a'})

    def test_inactive_subscription_not_counted(self):
        """A deactivated subscription is not counted as active."""
        sub = self.Sub.create({
            'user_id': self.user.id, 'endpoint': 'https://push/dead',
            'p256dh': 'k', 'auth': 'a'})
        sub.active = False
        self.assertEqual(
            len(self.user.push_subscription_ids.filtered('active')), 0)

    def test_push_staged_on_nudge(self):
        """A nudge stages a push for a subscribed user.

        Calls ``_stage_push`` directly rather than going through
        ``_deliver_simple``: the latter is overridden by rollout_internal
        with an activity-creation path that is broken independently of this
        module (see the note in the change's README).
        """
        self.Sub.create({
            'user_id': self.user.id, 'endpoint': 'https://push/live',
            'p256dh': 'k', 'auth': 'a'})
        nudge = self.env['rollout.nudge'].create({
            'name': 'Test nudge',
            'trigger_event': 'period_published',
            'template': 'Hej {user}',
            'project_id': self.env['rollout.project'].search([], limit=1).id,
        })
        nudge._stage_push(self.user, 'Hej')
        staged = self.Queue.search([('user_id', '=', self.user.id)])
        self.assertEqual(len(staged), 1)
        self.assertEqual(staged.state, 'pending')
        self.assertEqual(nudge.push_sent_count, 1)

    def test_push_anti_spam_cap(self):
        """The daily maximum suppresses further pushes."""
        self.env['ir.config_parameter'].sudo().set_param(
            'rollout_app.push_daily_max', 2)
        for i in range(3):
            self.Queue.create({
                'user_id': self.user.id,
                'title': f'N{i}', 'body': 'b'})
        self.assertFalse(
            self.env['rollout.nudge']._push_allowed(self.user))

    def test_push_allowed_under_cap(self):
        """Under the cap, push is allowed."""
        self.env['ir.config_parameter'].sudo().set_param(
            'rollout_app.push_daily_max', 5)
        self.assertTrue(
            self.env['rollout.nudge']._push_allowed(self.user))

    def test_push_send_without_pywebpush_does_not_raise(self):
        """Sending without a VAPID key logs and returns False, never raises."""
        sub = self.Sub.create({
            'user_id': self.user.id, 'endpoint': 'https://push/x',
            'p256dh': 'k', 'auth': 'a'})
        # No VAPID key configured in the test DB.
        self.assertFalse(sub._send('Title', 'Body'))

    def test_dispatch_drains_queue(self):
        """The dispatch cron marks staged items sent."""
        self.Queue.create({
            'user_id': self.user.id, 'title': 'T', 'body': 'B'})
        self.Sub.cron_rollout_push_dispatch()
        self.assertFalse(self.Queue.search([('state', '=', 'pending')]))


@tagged('post_install', '-at_install')
class TestRolloutAppEndToEnd(TransactionCase):
    """The whole loop: publish → see → complete → points → team → push.

    One participant, one week: a course line (static) and a survey line
    (periodic), the weekly rhythm, and the resulting standing.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Module = cls.env['rollout.module']
        cls.Line = cls.env['rollout.module.line']
        cls.App = cls.env['rollout.app']
        cls.AppLine = cls.env['rollout.app.line']

        cls.user = cls.env['res.users'].create({
            'name': 'Medarbetare', 'login': 'e2e_medarbetare'})
        cls.colleague = cls.env['res.users'].create({
            'name': 'Kollega', 'login': 'e2e_kollega'})

        cls.project = cls.env['rollout.project'].create({
            'name': 'E2E Project',
            'customer_id': cls.env['res.partner'].create(
                {'name': 'E2E Customer', 'is_company': True}).id,
            'state': 'active',
            'team_member_ids': [(6, 0, [cls.user.id, cls.colleague.id])],
        })
        cls.app = cls.App.create({
            'name': 'E2E App', 'project_id': cls.project.id})

    def test_full_week_loop(self):
        """Monday to Sunday, the whole loop, end to end."""
        # --- Sunday: the cron spawns next week's survey line ---------------
        survey_module = self.Module.create({
            'name': 'Vecko-enkät',
            'spawn_mode': 'periodic',
            'recurrence': 'weekly',
            'allowed_model': 'survey.survey',
            'clear_mode': 'auto',
            'default_points': 5,
            'default_coins': 2,
        })
        course_module = self.Module.create({
            'name': 'Kurs',
            'spawn_mode': 'static',
            'allowed_model': 'slide.channel',
            'clear_mode': 'auto',
            'default_points': 10,
            'default_coins': 5,
        })
        self.app.module_ids = [(6, 0, [survey_module.id, course_module.id])]

        spawned = self.Line.cron_rollout_app_spawn()
        survey_line = spawned.filtered(
            lambda l: l.module_id == survey_module)
        self.assertTrue(survey_line, "the cron must spawn a survey line")

        # A course line is configuration, created by hand.
        channel = self.env['slide.channel'].create({'name': 'CRM kap 1'})
        course_line = self.Line.create({
            'name': 'CRM kap 1',
            'module_id': course_module.id,
            'module_rel': f'slide.channel,{channel.id}',
        })

        # --- Monday 07:00: the lines become visible ------------------------
        self.assertTrue(survey_line.publish_at)
        visible = self.AppLine.search(
            self.AppLine._visible_domain(self.user))
        self.assertIn(course_line.app_line_ids.filtered(
            lambda l: l.user_id == self.user), visible)

        # --- The employee completes the course (automatic clearing) --------
        course_app_line = self.AppLine.search([
            ('module_line_id', '=', course_line.id),
            ('user_id', '=', self.user.id)], limit=1)
        # Simulate the source model appearing, then the auto-clear cron.
        self.env['slide.channel.partner'].create({
            'channel_id': channel.id,
            'partner_id': self.user.partner_id.id,
            'member_status': 'completed',
        })
        self.AppLine.cron_rollout_app_autoclear()
        self.assertEqual(course_app_line.state, 'done')
        self.assertTrue(course_app_line.source_ref)
        self.assertEqual(course_app_line.points_earned, 10)

        # --- The employee answers the survey (automatic clearing) ----------
        survey = self.env['survey.survey'].create({'title': 'Veckans enkät'})
        survey_line.module_rel = f'survey.survey,{survey.id}'
        # The spawn cron already generated the participant row; reuse it.
        survey_app_line = self.AppLine.search([
            ('module_line_id', '=', survey_line.id),
            ('user_id', '=', self.user.id)], limit=1)
        self.assertTrue(survey_app_line, "the cron must generate the row")
        self.env['survey.user_input'].create({
            'survey_id': survey.id,
            'partner_id': self.user.partner_id.id,
            'state': 'done',
        })
        self.AppLine.cron_rollout_app_autoclear()
        self.assertEqual(survey_app_line.state, 'done')
        self.assertEqual(survey_app_line.points_earned, 5)

        # --- Points, and the team standing ---------------------------------
        totals = self.app._get_personal_totals(self.user)
        self.assertEqual(totals['points'], 15)
        self.assertEqual(totals['coins'], 7)
        self.assertEqual(totals['done'], 2)

        # The colleague completed nothing, so the employee leads.
        standing = self.app._get_team_member_totals()
        self.assertEqual(standing[0]['user'], self.user)
        self.assertEqual(standing[0]['points'], 15)
        self.assertEqual(self.app._get_team_total(), 15)

        # --- A push reaches the employee -----------------------------------
        self.env['rollout.push.subscription'].create({
            'user_id': self.user.id,
            'endpoint': 'https://push/e2e',
            'p256dh': 'k', 'auth': 'a',
        })
        nudge = self.env['rollout.nudge'].create({
            'name': 'Veckans uppgifter',
            'trigger_event': 'period_published',
            'template': 'Hej {user}, veckans uppgifter är här',
            'project_id': self.project.id,
        })
        nudge._stage_push(self.user, 'Veckans uppgifter är här')
        staged = self.env['rollout.push.queue'].search([
            ('user_id', '=', self.user.id), ('state', '=', 'pending')])
        self.assertEqual(len(staged), 1)

        # --- Sunday: the period ends, the summary still sees it ------------
        survey_line.write({
            'period_start': '2020-01-06',
            'period_end': '2020-01-12',
        })
        # The completed line is retained in data regardless of the period.
        self.assertTrue(survey_app_line.exists())
