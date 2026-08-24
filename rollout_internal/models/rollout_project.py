"""Extend rollout.project with internal-specific behavior."""

from odoo import models


class RolloutProject(models.Model):
    _inherit = 'rollout.project'

    def action_activate(self):
        """Ensure perspective is set to internal when activating."""
        if self.perspective != 'internal':
            self.perspective = 'internal'
        return super().action_activate()
