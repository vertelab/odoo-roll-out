"""Bridge: rollout.project ↔ project.project for timesheet/Gantt integration."""

from odoo import models, fields, api


class RolloutProject(models.Model):
    _inherit = 'rollout.project'

    project_id = fields.Many2one(
        'project.project', string='Linked Project',
        help='Odoo project for timesheet, Gantt, and budget tracking')

    @api.model_create_multi
    def create(self, vals_list):
        projects = super().create(vals_list)
        for project in projects:
            if not project.project_id:
                project._create_linked_project()
        return projects

    def _create_linked_project(self):
        """Auto-create a project.project when a rollout.project is created."""
        if self.env['ir.module.module'].sudo().search(
                [('name', '=', 'project'), ('state', '=', 'installed')]):
            project = self.env['project.project'].create({
                'name': self.name,
                'user_id': self.manager_id.id,
                'date_start': self.date_start,
                'date': self.date_launch,
            })
            self.project_id = project.id


class RolloutPhase(models.Model):
    _inherit = 'rollout.phase'

    project_task_id = fields.Many2one(
        'project.task', string='Linked Milestone')

    @api.model_create_multi
    def create(self, vals_list):
        phases = super().create(vals_list)
        for phase in phases:
            if not phase.project_task_id and phase.project_id.project_id:
                phase._create_milestone_task()
        return phases

    def _create_milestone_task(self):
        """Create a milestone project.task for this ADKAR phase."""
        if self.project_id.project_id:
            task = self.env['project.task'].create({
                'name': f'{self.adkar_phase}: {self.name}',
                'project_id': self.project_id.project_id.id,
                'is_milestone': True,
                'date_deadline': self.date_end,
            })
            self.project_task_id = task.id
