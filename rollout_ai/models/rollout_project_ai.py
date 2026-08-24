"""Extend rollout.project with AI settings (goal sync + executive summary).

Defined in rollout_ai so they are co-located with the crons and views that
consume them, and available in both the external (consultant) and internal
(customer) perspectives when the AI bridge is installed.
"""

from odoo import models, fields


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
