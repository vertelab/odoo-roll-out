"""Extend rollout.project with AI settings (goal sync + executive summary).

Defined in rollout_ai so they are co-located with the crons and views that
consume them, and available in both the external (consultant) and internal
(customer) perspectives when the AI bridge is installed.
"""

import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class RolloutProject(models.Model):
    _inherit = 'rollout.project'

    # Executive summary frequency (for rollout_ai integration)
    executive_summary_frequency = fields.Selection([
        ('weekly', 'Weekly'),
        ('biweekly', 'Biweekly'),
        ('monthly', 'Monthly'),
    ], default='weekly', string='Summary Frequency')

    # Goal sync settings (for rollout_ai integration)
    goal_sync_frequency = fields.Selection([
        ('realtime', 'Real-time'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('manual', 'Manual'),
    ], default='weekly', string='Goal Sync Frequency')
    goal_auto_create = fields.Boolean('Auto-create Goals', default=False)
    goal_require_pm_approval = fields.Boolean('Require PM Approval', default=True)
    goal_notify_on_create = fields.Boolean('Notify on Create', default=True)

    # -- AI sentiment analysis -------------------------------------------

    def action_analyze_sentiment(self):
        """Button: run AI hotspot detection on this project's sentiment."""
        self.ensure_one()
        hotspots = self.env['rollout.sentiment.ai'].analyze_project(self)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Sentiment Analysis',
                'message': '%s hotspot(s) detected and flagged.'
                           % len(hotspots),
                'type': 'info' if hotspots else 'warning',
                'sticky': False,
            },
        }

    @api.model
    def cron_analyze_sentiment_hotspots(self):
        """Cron: analyze sentiment hotspots for all active projects."""
        projects = self.search([('state', '=', 'active')])
        analyzed = 0
        for project in projects:
            if project.sentiment_ids.filtered(lambda s: s.comment):
                self.env['rollout.sentiment.ai'].analyze_project(project)
                analyzed += 1
        _logger.info(
            "rollout_ai: analyzed sentiment for %s projects", analyzed)
        return analyzed
