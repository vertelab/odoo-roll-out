# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class RolloutPortfolio(models.AbstractModel):
    _name = 'rollout.portfolio'
    _description = 'Employee Portfolio (Aggregated CV View)'

    @api.model
    def get_employee_portfolio(self, employee_id):
        """Return structured portfolio data for an employee.

        Args:
            employee_id: hr.employee id or record

        Returns:
            dict with keys: employee, skills, courses, badges,
            adoption, rollouts
        """
        Employee = self.env.get('hr.employee')
        if not Employee:
            return {}
        employee = Employee.browse(employee_id)
        if not employee.exists():
            return {}

        return {
            'employee': self._get_employee_info(employee),
            'skills': self._get_skills(employee),
            'courses': self._get_courses(employee),
            'badges': self._get_badges(employee),
            'adoption': self._get_adoption(employee),
            'rollouts': self._get_rollouts(employee),
        }

    def _get_employee_info(self, employee):
        return {
            'id': employee.id,
            'name': employee.name,
            'department': employee.department_id.name or '',
            'job_title': employee.job_id.name or employee.job_title or '',
        }

    def _get_skills(self, employee):
        """Aggregate employee skills with certification data."""
        result = []
        for emp_skill in employee.employee_skill_ids:
            skill = emp_skill.skill_id
            result.append({
                'name': skill.name,
                'level': emp_skill.skill_level_id.name or '',
                'level_progress': emp_skill.skill_level_id.level_progress or 0,
                'certification_date': str(emp_skill.certification_date or ''),
                'expiration_date': str(emp_skill.expiration_date or ''),
                'standard': (
                    skill.mgmtsystem_standard_id.name
                    if hasattr(skill, 'mgmtsystem_standard_id') and
                       skill.mgmtsystem_standard_id
                    else ''
                ),
            })
        return result

    def _get_courses(self, employee):
        """Aggregate completed LMS courses."""
        result = []
        user = employee.user_id
        if not user or not user.partner_id:
            return result
        partner = user.partner_id

        # Query slide.channel.partner for completed courses (only if model exists)
        ChannelPartner = self.env.get('slide.channel.partner')
        if ChannelPartner:
            completions = ChannelPartner.search([
                ('partner_id', '=', partner.id),
                ('completed', '=', True),
            ])
            for comp in completions:
                result.append({
                    'name': comp.channel_id.name,
                    'completed_date': str(comp.create_date.date()),
                    'certification': (
                        comp.channel_id.certification_name
                        if hasattr(comp.channel_id, 'certification_name')
                        else ''
                    ),
                })
        return result

    def _get_badges(self, employee):
        """Aggregate earned gamification badges."""
        result = []
        user = employee.user_id
        if not user:
            return result

        BadgeUser = self.env.get('gamification.badge.user')
        if BadgeUser:
            badge_users = BadgeUser.search([('user_id', '=', user.id)])
            for bu in badge_users:
                result.append({
                    'name': bu.badge_id.name,
                    'level': bu.level or '',
                    'awarded_date': str(bu.create_date.date()),
                })
        return result

    def _get_adoption(self, employee):
        """Compute adoption metrics."""
        user = employee.user_id
        if not user:
            return {
                'login_streak': 0,
                'karma': 0,
                'tasks_completed': 0,
            }
        return {
            'login_streak': user.karma or 0,
            'karma': user.karma or 0,
            'tasks_completed': self.env['rollout.task'].search_count([
                ('assigned_to', '=', user.id),
                ('state', '=', 'done'),
            ]),
        }

    def _get_rollouts(self, employee):
        """Find rollouts the employee participates in."""
        result = []
        user = employee.user_id
        if not user:
            return result

        # Tasks assigned to this user
        tasks = self.env['rollout.task'].search([
            ('assigned_to', '=', user.id),
        ])
        project_ids = tasks.mapped('project_id')
        for project in project_ids:
            project_tasks = tasks.filtered(lambda t: t.project_id == project)
            done = len(project_tasks.filtered(lambda t: t.state == 'done'))
            total = len(project_tasks)
            result.append({
                'project': project.name,
                'role': '',
                'progress': round(done / total * 100, 1) if total else 0,
                'done': done,
                'total': total,
            })
        return result
