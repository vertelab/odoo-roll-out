"""Rollout Role — role-specific requirements for rollout projects."""

from odoo import models, fields


class RolloutRole(models.Model):
    _name = 'rollout.role'
    _description = 'Rollout Role'
    _order = 'name'

    project_id = fields.Many2one(
        'rollout.project', string='Project', required=True, ondelete='cascade')
    name = fields.Char('Role Name', required=True)
    description = fields.Text('Description')

    # Required skills for this role
    required_skill_ids = fields.One2many(
        'rollout.role.skill', 'role_id', string='Required Skills')

    # Required courses (via website_slides / LMS bridge)
    required_course_ids = fields.Many2many(
        'slide.channel', 'rollout_role_required_course_rel', 'role_id', 'course_id',
        string='Required Courses',
        help='LMS courses required for this role')

    # Required badges (via gamification bridge)
    required_badge_ids = fields.Many2many(
        'gamification.badge', 'rollout_role_required_badge_rel', 'role_id', 'badge_id',
        string='Required Badges',
        help='Gamification badges required for this role')

    # Task templates for onboarding
    task_template_ids = fields.One2many(
        'rollout.role.task.template', 'role_id',
        string='Task Templates')

    # Assigned employees
    employee_ids = fields.Many2many(
        'hr.employee', 'rollout_role_employee_rel', 'role_id', 'employee_id',
        string='Assigned Employees')

    # Phase scoping
    phase_ids = fields.Many2many(
        'rollout.phase', 'rollout_role_phase_rel', 'role_id', 'phase_id',
        string='Active in Phases')


class RolloutRoleSkill(models.Model):
    _name = 'rollout.role.skill'
    _description = 'Role Skill Requirement'

    role_id = fields.Many2one('rollout.role', required=True, ondelete='cascade')
    skill_id = fields.Many2one('hr.skill', string='Skill', required=True)
    required_level = fields.Char('Required Level')


class RolloutRoleTaskTemplate(models.Model):
    _name = 'rollout.role.task.template'
    _description = 'Role Task Template'

    role_id = fields.Many2one('rollout.role', required=True, ondelete='cascade')
    name = fields.Char('Task Name', required=True)
    description = fields.Text('Description')
    sequence = fields.Integer('Sequence', default=10)
