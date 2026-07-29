# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel Sverige AB
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Rollout — LMS Bridge',
    'version': '18.0.1.0.0',
    'summary': 'eLearning course integration for rollout roles and competency targets.',
    'category': 'Productivity',
    'author': 'Vertel Sverige AB',
    'website': 'https://vertel.se',
    'license': 'AGPL-3',
    'depends': ['rollout', 'website_slides'],
    'data': [
        'views/rollout_lms_views.xml',
    ],
    'installable': True,
    'auto_install': True,
    'application': False,
}
