# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel Sverige AB
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Rollout — Management System Bridge',
    'version': '18.0.1.0.0',
    'summary': 'ISO management system integration for rollout projects.',
    'category': 'Productivity',
    'author': 'Vertel Sverige AB',
    'website': 'https://vertel.se',
    'license': 'AGPL-3',
    'depends': ['rollout', 'mgmtsystem'],
    'data': [
        'views/rollout_mgmtsystem_views.xml',
    ],
    'installable': True,
    'auto_install': True,
    'application': False,
}
