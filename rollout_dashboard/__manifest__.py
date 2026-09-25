# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel Sverige AB
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Rollout — Dashboard Bridge',
    'version': '18.0.1.0.0',
    'summary': 'BI dashboards for rollout adoption, sentiment, risk, and readiness.',
    'description': '''
Rollout — Dashboard Bridge
==========================

    BI dashboards for rollout adoption, sentiment, risk, and readiness.

    Features:

        - Demo Data: Ships pre-configured demo data for the industry.
    ''',
    'category': 'Productivity',
    'author': 'Vertel Sverige AB',
    'website': 'https://vertel.se/apps/odoo-roll-out/rollout_dashboard',
    'license': 'AGPL-3',
    'depends': ['rollout', 'dashboard_vrtl'],
    'data': [
        'data/rollout_dashboard_data.xml',
    ],
    'installable': True,
    'auto_install': True,
    'application': False,
}
