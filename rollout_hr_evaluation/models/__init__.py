"""Bridge: rollout.competency.target ↔ hr.evaluation for employee reviews."""

from odoo import models, fields, api


class RolloutCompetencyTarget(models.Model):
    _inherit = 'rollout.competency.target'

    evaluation_goal_ids = fields.One2many(
        'hr.evaluation.goal', 'rollout_target_id',
        string='Linked Evaluation Goals')


class HrEvaluationGoal(models.Model):
    _inherit = 'hr.evaluation.goal'

    rollout_target_id = fields.Many2one(
        'rollout.competency.target', string='Rollout Competency Target',
        readonly=True, ondelete='set null')
    is_rollout_goal = fields.Boolean(
        'Rollout Goal', related='rollout_target_id.id', store=True)

    @api.onchange('rollout_target_id')
    def _onchange_rollout_target(self):
        if self.rollout_target_id:
            self.name = self.rollout_target_id.name
            self.target = self.rollout_target_id.level or 'Achieve target level'


class HrEvaluation(models.Model):
    _inherit = 'hr.evaluation'

    def _auto_populate_rollout_goals(self):
        """Add rollout competency targets as evaluation goals."""
        employee = self.employee_id
        if not employee:
            return

        # Find rollout targets for this employee's roles
        roles = self.env['rollout.role'].search([
            ('employee_ids', 'in', employee.id),
        ])
        targets = self.env['rollout.competency.target'].search([
            ('role_id', 'in', roles.ids),
            ('state', 'in', ['planned', 'in_progress', 'at_risk']),
        ])

        for target in targets:
            if not self.env['hr.evaluation.goal'].search([
                ('evaluation_id', '=', self.id),
                ('rollout_target_id', '=', target.id),
            ]):
                self.env['hr.evaluation.goal'].create({
                    'evaluation_id': self.id,
                    'rollout_target_id': target.id,
                    'name': target.name,
                    'target': target.level or 'Achieve competency',
                })
