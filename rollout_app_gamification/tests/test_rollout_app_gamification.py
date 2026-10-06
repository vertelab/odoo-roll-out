# -*- coding: utf-8 -*-
# Part of Vertel. See LICENSE file for full copyright and licensing details.

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRolloutAppGamification(TransactionCase):
    """Karma for completed lines, and achievement-gated unlocking."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.Module = cls.env['rollout.module']
        cls.Line = cls.env['rollout.module.line']
        cls.App = cls.env['rollout.app']
        cls.AppLine = cls.env['rollout.app.line']

        cls.user_a = cls.env['res.users'].create({
            'name': 'Gami A', 'login': 'gami_a'})
        cls.user_b = cls.env['res.users'].create({
            'name': 'Gami B', 'login': 'gami_b'})

        cls.project = cls.env['rollout.project'].create({
            'name': 'Gami Project',
            'customer_id': cls.env['res.partner'].create(
                {'name': 'Gami Customer', 'is_company': True}).id,
            'state': 'active',
            'team_member_ids': [(6, 0, [cls.user_a.id, cls.user_b.id])],
        })
        cls.app = cls.App.create({
            'name': 'Gami App',
            'project_id': cls.project.id,
        })
        cls.module = cls.Module.create({
            'name': 'Kurs',
            'spawn_mode': 'static',
            'default_points': 10,
            'default_coins': 5,
        })
        cls.app.module_ids = [(6, 0, [cls.module.id])]

    def _line_for(self, line, user):
        return self.AppLine.search([
            ('module_line_id', '=', line.id),
            ('user_id', '=', user.id)], limit=1)

    # ------------------------------------------------------------------
    # 4.1 Auto-install
    # ------------------------------------------------------------------
    def test_bridge_installed(self):
        """The bridge is installed (it is auto_install)."""
        module = self.env['ir.module.module'].search([
            ('name', '=', 'rollout_app_gamification')], limit=1)
        self.assertEqual(module.state, 'installed')

    # ------------------------------------------------------------------
    # 4.2 Karma
    # ------------------------------------------------------------------
    def test_karma_awarded_on_completion(self):
        """Completing a line awards karma equal to its points."""
        line = self.Line.create({
            'name': 'CRM kap 3', 'module_id': self.module.id})
        app_line = self._line_for(line, self.user_a)
        karma_before = self.user_a.karma
        app_line.action_mark_done()
        self.assertEqual(self.user_a.karma, karma_before + 10)

    def test_karma_awarded_once(self):
        """Completing twice does not award karma twice."""
        line = self.Line.create({
            'name': 'CRM kap 4', 'module_id': self.module.id})
        app_line = self._line_for(line, self.user_a)
        karma_before = self.user_a.karma
        app_line.action_mark_done()
        app_line.action_mark_done()
        self.assertEqual(self.user_a.karma, karma_before + 10)

    def test_karma_awarded_to_the_completing_user(self):
        """Karma goes to the person who completed, not the team."""
        line = self.Line.create({
            'name': 'CRM kap 5', 'module_id': self.module.id})
        before_a = self.user_a.karma
        before_b = self.user_b.karma
        self._line_for(line, self.user_a).action_mark_done()
        self.assertEqual(self.user_a.karma, before_a + 10)
        self.assertEqual(self.user_b.karma, before_b)

    # ------------------------------------------------------------------
    # 4.3 Unlocking
    # ------------------------------------------------------------------
    def test_unlock_on_gating_line_completion(self):
        """Completing a gating line unlocks the advanced line for that person
        only."""
        basic = self.Line.create({
            'name': 'CRM kap 1', 'module_id': self.module.id})
        advanced = self.Line.create({
            'name': 'Fördjupning CRM kap 2',
            'module_id': self.module.id,
            'state': 'locked',
            'source_line_id': basic.id,
        })
        # Both people start locked on the advanced line.
        a_advanced = self._line_for(advanced, self.user_a)
        b_advanced = self._line_for(advanced, self.user_b)
        self.assertTrue(a_advanced.locked)
        self.assertTrue(b_advanced.locked)

        # Only A completes the basic line.
        self._line_for(basic, self.user_a).action_mark_done()

        self.assertFalse(a_advanced.locked)
        self.assertTrue(b_advanced.locked)

    # ------------------------------------------------------------------
    # 4.4 Badges are not created by the app
    # ------------------------------------------------------------------
    def test_no_badge_created_on_completion(self):
        """Completing a line creates no badge."""
        badge = self.env['gamification.badge'].create({'name': 'Test Badge'})
        line = self.Line.create({
            'name': 'Badge line', 'module_id': self.module.id,
            'badge_id': badge.id})
        BadgeUser = self.env['gamification.badge.user']
        before = BadgeUser.search_count([])
        self._line_for(line, self.user_a).action_mark_done()
        self.assertEqual(BadgeUser.search_count([]), before)

    def test_badge_is_a_display_link(self):
        """The line's badge is stored as a reference, nothing more."""
        badge = self.env['gamification.badge'].create({'name': 'Display Badge'})
        line = self.Line.create({
            'name': 'Display line', 'module_id': self.module.id,
            'badge_id': badge.id})
        self.assertEqual(line.badge_id, badge)

    # ------------------------------------------------------------------
    # 4.5 Works without gamification
    # ------------------------------------------------------------------
    def test_points_visible_without_gamification(self):
        """The app's own points record exists independently of karma."""
        line = self.Line.create({
            'name': 'Own points', 'module_id': self.module.id})
        app_line = self._line_for(line, self.user_a)
        app_line.action_mark_done()
        self.assertEqual(app_line.points_earned, 10)
        self.assertEqual(self.app._get_personal_totals(self.user_a)['points'], 10)
