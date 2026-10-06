# -*- coding: utf-8 -*-
# Part of Vertel. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class RolloutModule(models.Model):
    """A content type — the contract for a kind of menu item.

    The type owns what its lines may point at (``allowed_model``), how they
    are created (``spawn_mode``), and what they are worth.
    """

    _name = 'rollout.module'
    _description = 'Rollout App Module Type'
    _order = 'sequence, name'

    name = fields.Char('Name', required=True, translate=True)
    description = fields.Text('Description', translate=True)
    sequence = fields.Integer('Sequence', default=10)
    active = fields.Boolean('Active', default=True)

    allowed_model = fields.Char(
        'Allowed Model',
        help="The only model this type's lines may reference, e.g. "
             "'slide.channel'. Leave empty to allow any model (used for "
             "manual, self-reported types with no backing record).")

    spawn_mode = fields.Selection([
        ('static', 'Static — exists from configuration, waits until done'),
        ('periodic', 'Periodic — a new line is created each period'),
    ], string='Spawn Mode', default='static', required=True,
        help="Static: the line is created once and never closes. "
             "Periodic: a cron creates a new line each period, and the line "
             "leaves the view when the period ends.")

    recurrence = fields.Selection([
        ('none', 'None'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ], string='Recurrence', default='none',
        help="Only used when the spawn mode is periodic.")

    lead_time = fields.Integer(
        'Lead Time (periods)', default=1,
        help="How many periods ahead the spawn cron creates lines, so the "
             "menu is populated before the period begins.")

    clear_mode = fields.Selection([
        ('auto', 'Automatic — read the source model'),
        ('manual', 'Manual — the person reports it'),
        ('either', 'Either'),
    ], string='Completion Mode', default='manual', required=True,
        help="Automatic completion reads the source model (e.g. a course "
             "completion). Manual lets the person mark it done.")

    default_points = fields.Integer('Default Points', default=10)
    default_coins = fields.Integer('Default Coins', default=5)

    line_ids = fields.One2many(
        'rollout.module.line', 'module_id', string='Lines')
    line_count = fields.Integer('Lines', compute='_compute_line_count')

    @api.depends('line_ids')
    def _compute_line_count(self):
        for module in self:
            module.line_count = len(module.line_ids)

    @api.constrains('allowed_model')
    def _check_allowed_model(self):
        """Warn if the declared model is unknown.

        Deliberately not an error: a type may reference a model from a
        module that is not installed yet (e.g. 'slide.channel' before
        website_slides). The real gate is the line-level constraint, which
        compares an actual reference against this value.
        """
        for module in self:
            if not module.allowed_model:
                continue
            if module.allowed_model not in self.env.registry.models:
                _logger.info(
                    "rollout_app: module type '%s' declares unknown model "
                    "'%s' (is its providing module installed?)",
                    module.name, module.allowed_model)

    @api.constrains('spawn_mode', 'recurrence')
    def _check_recurrence_required(self):
        """A periodic type must have a recurrence."""
        for module in self:
            if module.spawn_mode == 'periodic' and module.recurrence == 'none':
                raise ValidationError(_(
                    "A periodic module must have a recurrence."))
