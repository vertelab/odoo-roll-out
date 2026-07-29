# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class RolloutRole(models.Model):
    _name = 'rollout.role'
    _description = 'Rollout Role'
    _order = 'name'

    name = fields.Char(required=True, translate=True)
    active = fields.Boolean(default=True)
    description = fields.Html(translate=True)

    # ── Competency Requirements (core: uses hr.skill when hr_skills installed) ──
    # Note: course_ids and badge_ids are added by bridge modules
    # (rollout_lms adds course_ids → slide.channel,
    #  rollout_gamification adds badge_ids → gamification.badge)

    # ── Task Templates ──
    task_template_ids = fields.One2many(
        'rollout.task.template', 'role_id', string='Task Templates',
    )


class RolloutTaskTemplate(models.Model):
    _name = 'rollout.task.template'
    _description = 'Rollout Task Template'
    _order = 'sequence, id'

    name = fields.Char(required=True, translate=True)
    role_id = fields.Many2one(
        'rollout.role', required=True, ondelete='cascade',
    )
    sequence = fields.Integer(default=10)
    description = fields.Html(translate=True)
    deadline_days = fields.Integer(
        default=7, string='Days After Assignment',
    )
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Medium'),
        ('2', 'High'),
        ('3', 'Urgent'),
    ], default='1')
