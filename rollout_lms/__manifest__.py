# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel Sverige AB
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Rollout — LMS Bridge',
    'version': '18.0.1.0.0',
    'summary': 'ELearning course integration for rollout roles and competency targets.',
    'description': '''
Rollout — LMS Bridge
====================

    ELearning course integration for rollout roles and competency targets.

    Features:

        - UI Integration: Extends 1 view(s) in the Odoo interface.
        - Extends Odoo: Builds on slide.channel.
    ''',
    'category': 'Productivity',
    'author': 'Vertel Sverige AB',
    'website': 'https://vertel.se/apps/odoo-roll-out/rollout_lms',
    'license': 'AGPL-3',
    'depends': ['rollout', 'website_slides'],
    'data': [
        'views/rollout_lms_views.xml',
    ],
    'installable': True,
    'auto_install': True,
    'application': False,
}
