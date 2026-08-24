"""Rollout Organizational Change — model org changes during rollout."""

from odoo import models, fields


class RolloutOrgChange(models.Model):
    _name = 'rollout.org.change'
    _description = 'Rollout Organizational Change'
    _order = 'create_date desc'

    project_id = fields.Many2one(
        'rollout.project', string='Project', required=True, ondelete='cascade')
    phase_id = fields.Many2one(
        'rollout.phase', string='Phase', ondelete='set null')

    name = fields.Char('Change Name', required=True)
    change_type = fields.Selection([
        ('new_dept', 'New Department'),
        ('restructure', 'Restructure'),
        ('new_role', 'New Role'),
        ('merge', 'Merge'),
        ('split', 'Split'),
        ('reporting', 'Reporting Change'),
        ('other', 'Other'),
    ], required=True, string='Change Type')
    description = fields.Text('Description')

    state = fields.Selection([
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ], default='planned', required=True)

    # Optional HR links
    department_ids = fields.Many2many(
        'hr.department', 'rollout_org_change_department_rel', 'org_change_id', 'department_id',
        string='Affected Departments')
    job_ids = fields.Many2many(
        'hr.job', 'rollout_org_change_job_rel', 'org_change_id', 'job_id',
        string='Affected Jobs')
    employee_ids = fields.Many2many(
        'hr.employee', 'rollout_org_change_employee_rel', 'org_change_id', 'employee_id',
        string='Affected Employees')
