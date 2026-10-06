# -*- coding: utf-8 -*-
# Part of Vertel. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class RolloutApp(models.Model):
    """A project's menu — the app a participant opens.

    One per project. The team is the project's ``team_member_ids``; there is
    no separate team model.
    """

    _name = 'rollout.app'
    _description = 'Rollout App'
    _inherit = ['mail.thread']
    _order = 'name'

    name = fields.Char('Name', required=True, translate=True)
    project_id = fields.Many2one(
        'rollout.project', string='Project', required=True,
        ondelete='cascade', index=True)
    active = fields.Boolean('Active', default=True)

    module_ids = fields.Many2many(
        'rollout.module', 'rollout_app_module_rel', 'app_id', 'module_id',
        string='Modules')
    line_ids = fields.One2many(
        'rollout.module.line', compute='_compute_line_ids',
        string='Lines', readonly=True)
    app_line_ids = fields.One2many(
        'rollout.app.line', 'app_id', string='Participant Lines')

    _sql_constraints = [
        ('one_app_per_project', 'UNIQUE(project_id)',
         'A project can only have one app.'),
    ]

    @api.depends('module_ids')
    def _compute_line_ids(self):
        """The lines belonging to this app's modules."""
        for app in self:
            app.line_ids = self.env['rollout.module.line'].search([
                ('module_id', 'in', app.module_ids.ids),
            ])

    @api.constrains('project_id')
    def _check_project(self):
        for app in self:
            if not app.project_id:
                raise ValidationError(_("An app must belong to a project."))

    # ------------------------------------------------------------------
    # Aggregation
    # ------------------------------------------------------------------
    def _get_team_members(self):
        """The app's team — the project's team members."""
        self.ensure_one()
        return self.project_id.team_member_ids

    def _get_personal_totals(self, user=None):
        """Points and coins earned by one person in this app."""
        self.ensure_one()
        user = user or self.env.user
        lines = self.app_line_ids.filtered(lambda l: l.user_id == user)
        return {
            'points': sum(lines.mapped('points_earned')),
            'coins': sum(lines.mapped('coins_earned')),
            'done': len(lines.filtered(lambda l: l.state == 'done')),
            'open': len(lines.filtered(lambda l: l.state == 'open')),
        }

    def _get_team_total(self):
        """The combined points of the whole team."""
        self.ensure_one()
        return sum(self.app_line_ids.mapped('points_earned'))

    def _get_team_member_totals(self):
        """Per-member point totals, for the team view."""
        self.ensure_one()
        members = self._get_team_members()
        result = []
        for member in members:
            lines = self.app_line_ids.filtered(lambda l: l.user_id == member)
            result.append({
                'user': member,
                'points': sum(lines.mapped('points_earned')),
                'coins': sum(lines.mapped('coins_earned')),
                'done': len(lines.filtered(lambda l: l.state == 'done')),
            })
        return sorted(result, key=lambda r: r['points'], reverse=True)

    def action_open_app(self):
        """Open the personal app view."""
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'rollout_app.client',
            'name': self.name,
            'context': {'default_app_id': self.id},
        }
