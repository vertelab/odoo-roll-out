# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel Sverige AB
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Rollout — BPM Bridge',
    'version': '18.0.1.0.0',
    'summary': 'BPMN process engine integration for rollout projects.',
    'category': 'Productivity',
    'author': 'Vertel Sverige AB',
    'website': 'https://vertel.se',
    'license': 'AGPL-3',
    'depends': ['rollout', 'bpm_workflow'],
    'data': [
        'views/rollout_bpm_views.xml',
    ],
    'installable': True,
    'auto_install': True,
    'application': False,
}
