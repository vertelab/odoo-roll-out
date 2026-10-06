# -*- coding: utf-8 -*-
# Part of Vertel. See LICENSE file for full copyright and licensing details.

import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """Create an app for each active project and generate participant lines.

    Idempotent: an app already present for a project is left alone.
    """
    App = env['rollout.app']
    Module = env['rollout.module']

    projects = env['rollout.project'].search([('state', '=', 'active')])
    created = 0
    for project in projects:
        if App.search([('project_id', '=', project.id)], limit=1):
            continue
        App.create({
            'name': project.name,
            'project_id': project.id,
            'module_ids': [(6, 0, Module.search([]).ids)],
        })
        created += 1

    # Generate participant lines for every existing static line.
    ModuleLine = env['rollout.module.line']
    for line in ModuleLine.search([
            ('module_id.spawn_mode', '=', 'static')]):
        ModuleLine._generate_app_lines(line)

    _logger.info("rollout_app: created %s app(s) for active projects", created)
