# -*- coding: utf-8 -*-
# Part of Vertel. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class RolloutPushQueue(models.Model):
    """A staged push notification, waiting for the dispatch cron.

    The bus is not durable, so a notification that must survive until a cron
    runs is staged here first.
    """

    _name = 'rollout.push.queue'
    _description = 'Rollout Push Queue'
    _order = 'create_date'

    user_id = fields.Many2one(
        'res.users', string='User', required=True, ondelete='cascade',
        index=True)
    title = fields.Char('Title', required=True)
    body = fields.Text('Body', required=True)
    url = fields.Char('Link')

    state = fields.Selection([
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ], string='Status', default='pending', required=True, index=True)

    nudge_id = fields.Many2one('rollout.nudge', string='Nudge')

    @classmethod
    def _stage(cls, env, user, title, body, url=None, nudge=None):
        """Stage a notification for the next dispatch run."""
        return env['rollout.push.queue'].create({
            'user_id': user.id,
            'title': title,
            'body': body,
            'url': url,
            'nudge_id': nudge.id if nudge else False,
        })
