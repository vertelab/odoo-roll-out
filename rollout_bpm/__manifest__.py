# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel Sverige AB
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Rollout — BPM Bridge',
    'version': '18.0.1.0.0',
    'summary': 'BPMN process engine integration for rollout projects.',
    'description': '''
Rollout — BPM Bridge
====================

    BPMN process engine integration for rollout projects.

    Features:

        - UI Integration: Extends 1 view(s) in the Odoo interface.
        - Extends Odoo: Builds on bpm.instance, bpm.workflow, rollout.project.
    ''',
    'category': 'Productivity',
    'author': 'Vertel Sverige AB',
    'website': 'https://vertel.se/apps/odoo-roll-out/rollout_bpm',
    'license': 'AGPL-3',
    'depends': ['rollout', 'bpm_workflow'],
    'data': [
        'views/rollout_bpm_views.xml',
    ],
    'installable': True,
    'auto_install': True,
    'application': False,
}
