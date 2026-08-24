"""Bridge: rollout.role ↔ gamification.badge for competency tracking."""

from odoo import models, fields, api


class RolloutRole(models.Model):
    _inherit = 'rollout.role'

    challenge_id = fields.Many2one(
        'gamification.challenge', string='Linked Challenge')

    def action_create_challenge(self):
        """Create a gamification challenge for this role."""
        for role in self:
            if not role.challenge_id:
                challenge = self.env['gamification.challenge'].create({
                    'name': f'Rollout: {role.name}',
                    'description': f'Complete all requirements for the {role.name} role.',
                    'reward_ids': [(6, 0, role.required_badge_ids.ids)],
                })
                role.challenge_id = challenge.id


class RolloutCompetencyTarget(models.Model):
    _inherit = 'rollout.competency.target'

    def _compute_current_count(self):
        """Enhanced count using gamification badge completion."""
        res = super()._compute_current_count()
        # If gamification is installed, check badge completions too
        for target in self:
            if target.role_id and target.role_id.required_badge_ids:
                badge_users = self.env['gamification.badge.user'].search([
                    ('badge_id', 'in', target.role_id.required_badge_ids.ids),
                    ('badge_id.name', 'ilike', target.skill_id.name or ''),
                ])
                badge_count = len(badge_users.mapped('user_id'))
                target.current_count = max(target.current_count, badge_count)
        return res
