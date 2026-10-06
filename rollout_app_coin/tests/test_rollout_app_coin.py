# -*- coding: utf-8 -*-
# Part of Vertel. See LICENSE file for full copyright and licensing details.

from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRolloutAppCoin(TransactionCase):
    """Coins are credited on completion, once, and traceably."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.Module = cls.env['rollout.module']
        cls.Line = cls.env['rollout.module.line']
        cls.App = cls.env['rollout.app']
        cls.AppLine = cls.env['rollout.app.line']
        cls.CoinTracking = cls.env['gamification.coin.tracking']

        cls.user = cls.env['res.users'].create({
            'name': 'Coin Participant', 'login': 'coin_participant'})
        cls.project = cls.env['rollout.project'].create({
            'name': 'Coin Project',
            'customer_id': cls.env['res.partner'].create(
                {'name': 'Coin Customer', 'is_company': True}).id,
            'state': 'active',
            'team_member_ids': [(6, 0, [cls.user.id])],
        })
        cls.app = cls.App.create({
            'name': 'Coin App', 'project_id': cls.project.id})
        cls.module = cls.Module.create({
            'name': 'Kurs',
            'spawn_mode': 'static',
            'default_points': 10,
            'default_coins': 5,
        })
        cls.app.module_ids = [(6, 0, [cls.module.id])]

    def _app_line(self, name='CRM kap 3', coins=None):
        values = {'name': name, 'module_id': self.module.id}
        if coins is not None:
            values['coins'] = coins
        line = self.Line.create(values)
        return self.AppLine.search([
            ('module_line_id', '=', line.id),
            ('user_id', '=', self.user.id)], limit=1)

    # ------------------------------------------------------------------
    # 1.1 Auto-install
    # ------------------------------------------------------------------
    def test_bridge_installed(self):
        """The bridge auto-installs with both parents present."""
        module = self.env['ir.module.module'].search([
            ('name', '=', 'rollout_app_coin')], limit=1)
        self.assertEqual(module.state, 'installed')

    # ------------------------------------------------------------------
    # 2.1 Crediting
    # ------------------------------------------------------------------
    def test_coins_credited_on_completion(self):
        """Completing a line credits its coins."""
        app_line = self._app_line()
        before = self.user.coin_balance
        app_line.action_mark_done()
        self.assertEqual(self.user.coin_balance, before + 5)

    def test_coins_credited_once(self):
        """Completing twice does not credit twice."""
        app_line = self._app_line('CRM kap 4')
        app_line.action_mark_done()
        balance = self.user.coin_balance
        app_line.action_mark_done()
        self.assertEqual(self.user.coin_balance, balance)

    # ------------------------------------------------------------------
    # 2.2 Zero coins
    # ------------------------------------------------------------------
    def test_zero_coins_creates_no_entry(self):
        """A line worth nothing creates no ledger entry."""
        app_line = self._app_line('No coins', coins=0)
        before = self.CoinTracking.search_count([])
        app_line.action_mark_done()
        self.assertEqual(self.CoinTracking.search_count([]), before)

    # ------------------------------------------------------------------
    # 2.4 Reason
    # ------------------------------------------------------------------
    def test_reason_names_the_task(self):
        """The ledger entry's reason names the completed task."""
        app_line = self._app_line('CRM kap 5')
        app_line.action_mark_done()
        entry = self.CoinTracking.search([
            ('user_id', '=', self.user.id),
            ('gain', '>', 0)], limit=1)
        self.assertIn('CRM kap 5', entry.reason)

    # ------------------------------------------------------------------
    # 2.5 Traceability
    # ------------------------------------------------------------------
    def test_origin_ref_points_to_line(self):
        """The ledger entry resolves back to the app line."""
        app_line = self._app_line('CRM kap 6')
        app_line.action_mark_done()
        entry = self.CoinTracking.search([
            ('user_id', '=', self.user.id),
            ('gain', '>', 0)], limit=1)
        self.assertEqual(entry.origin_ref, app_line)
        self.assertEqual(entry.gain, 5)

    # ------------------------------------------------------------------
    # 3.1 Karma and coins together
    # ------------------------------------------------------------------
    def test_points_and_coins_awarded_separately(self):
        """One completion awards karma and coins, independently."""
        app_line = self._app_line('CRM kap 7')
        karma_before = self.user.karma
        coins_before = self.user.coin_balance
        app_line.action_mark_done()
        self.assertEqual(self.user.karma, karma_before + 10)
        self.assertEqual(self.user.coin_balance, coins_before + 5)

    # ------------------------------------------------------------------
    # 3.2 Coins do not touch karma
    # ------------------------------------------------------------------
    def test_coins_do_not_affect_karma(self):
        """Crediting coins leaves karma and rank alone."""
        app_line = self._app_line('CRM kap 8')
        app_line.action_mark_done()
        karma_after_completion = self.user.karma
        rank_after = self.user.rank_id
        # Spend coins; karma must not move.
        self.user._add_coins(-2, reason='Test spend')
        self.assertEqual(self.user.karma, karma_after_completion)
        self.assertEqual(self.user.rank_id, rank_after)

    # ------------------------------------------------------------------
    # 3.4 Coins recorded without the currency module
    # ------------------------------------------------------------------
    def test_coins_earned_recorded_on_line(self):
        """The line keeps its own record of coins earned."""
        app_line = self._app_line('CRM kap 9')
        app_line.action_mark_done()
        self.assertEqual(app_line.coins_earned, 5)

    # ------------------------------------------------------------------
    # 4.1 No shop dependency
    # ------------------------------------------------------------------
    def test_bridge_does_not_reference_shop(self):
        """The bridge knows nothing about the shop."""
        manifest = self.env['ir.module.module'].search([
            ('name', '=', 'rollout_app_coin')], limit=1)
        self.assertNotIn('gamification_coin_reward', manifest.dependencies_id.mapped('name'))

    # ------------------------------------------------------------------
    # 5.1 Non-negative validation
    # ------------------------------------------------------------------
    def test_negative_coins_earned_refused(self):
        """A negative coins_earned is refused by the constraint."""
        app_line = self._app_line('CRM kap 10')
        with self.assertRaises(Exception):
            app_line.write({'coins_earned': -5})

    # ------------------------------------------------------------------
    # 4.3 Balance usable when the shop arrives later
    # ------------------------------------------------------------------
    def test_balance_usable_after_later_install(self):
        """Coins earned before any shop exists are spendable later.

        The shop is a separate module; a balance is not tied to it. This
        asserts the balance is a plain number that a later consumer can use.
        """
        app_line = self._app_line('Earned before shop')
        app_line.action_mark_done()
        balance = self.user.coin_balance
        self.assertEqual(balance, 5)
        # The balance is a real ledger-derived number, not a placeholder.
        latest = self.CoinTracking.search([
            ('user_id', '=', self.user.id)],
            order='tracking_date desc, id desc', limit=1)
        self.assertEqual(latest.new_value, balance)
