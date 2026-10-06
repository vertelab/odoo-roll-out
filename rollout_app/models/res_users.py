# -*- coding: utf-8 -*-
# Part of Vertel. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    push_subscription_ids = fields.One2many(
        'rollout.push.subscription', 'user_id', string='Push Subscriptions')
    push_subscription_count = fields.Integer(
        'Active Subscriptions', compute='_compute_push_subscription_count')

    @api.depends('push_subscription_ids')
    def _compute_push_subscription_count(self):
        for user in self:
            user.push_subscription_count = len(
                user.push_subscription_ids.filtered('active'))

    @api.model
    def _get_rollout_apps(self):
        """The apps this user participates in."""
        return self.env['rollout.app'].search([
            ('project_id.team_member_ids', 'in', self.id),
        ])

    def _get_rollout_app_summary(self):
        """The data the app view needs, for this user.

        Returns a list of apps with the person's visible lines, their
        totals, and the team standing.
        """
        self.ensure_one()
        result = []
        for app in self._get_rollout_apps():
            visible = self.env['rollout.app.line'].search(
                app._visible_domain(self))
            result.append({
                'app_id': app.id,
                'name': app.name,
                'totals': app._get_personal_totals(self),
                'team_total': app._get_team_total(),
                'lines': [{
                    'id': line.id,
                    'name': line.name,
                    'state': line.state,
                    'locked': line.locked,
                    'points': line.points,
                    'coins': line.coins,
                    'missed': line._is_missed(),
                } for line in visible],
            })
        return result
