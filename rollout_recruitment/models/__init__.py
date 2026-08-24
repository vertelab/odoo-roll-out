"""Bridge: rollout.competency.target → hr.job for hiring recommendations."""

from odoo import models, fields, api


class RolloutCompetencyTarget(models.Model):
    _inherit = 'rollout.competency.target'

    job_id = fields.Many2one('hr.job', string='Linked Job Position')
    hiring_recommendation = fields.Boolean('Hiring Recommended',
                                           compute='_compute_hiring_recommendation')

    @api.depends('gap', 'deadline')
    def _compute_hiring_recommendation(self):
        today = fields.Date.context_today(self)
        for target in self:
            target.hiring_recommendation = (
                target.gap > 0
                and target.deadline
                and (target.deadline - today).days <= 30
            )

    def action_create_job(self):
        """Create an hr.job position from this competency target."""
        self.ensure_one()
        if not self.job_id:
            job = self.env['hr.job'].create({
                'name': f'{self.skill_id.name or self.name} Specialist',
                'description': (
                    f'Required for rollout: {self.project_id.name}\n'
                    f'Skill: {self.skill_id.name}\n'
                    f'Level: {self.level}\n'
                    f'Number of positions: {self.gap}'),
                'no_of_recruitment': self.gap,
            })
            self.job_id = job.id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.job',
            'res_id': self.job_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
