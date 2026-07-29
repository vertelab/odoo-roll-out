# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Rollout — Organizational Change & Adoption Platform',
    'version': '18.0.1.0.0',
    'summary': 'Beteendevetenskaplig Odoo-rollout med ADKAR, risk, kompetensmål, nudging och plangranskning.',
    'category': 'Productivity',
    'description': """
Rollout — Organizational Change & Adoption Platform
====================================================

Orchestrate behavioral science-driven Odoo implementations with:

- **ADKAR Phases**: Awareness, Desire, Knowledge, Ability, Reinforcement
  with forward/backward timeline planning and gates
- **Risk Register**: Probability × impact scoring, mitigation plans, trigger events
- **Competency Targets**: "We need 3 people with skill X at level Y by date Z"
  with automatic gap tracking against employee skills
- **Strategies**: Internal reassignment, external recruitment, training, consultants
  with cost, lead time, and achievement tracking
- **Scenarios**: Compare alternative timelines, competency approaches, and budgets
- **Sentiment Analysis**: Pulse surveys with AI hotspot detection
- **Behavioral Nudging**: Template-based nudges triggered by events
  (social proof, loss aversion, defaults)
- **Plan Review**: Multi-dimensional evaluation across 9 dimensions
  with 42 criteria and readiness scoring
- **Employee Portfolio**: Aggregated CV view of skills, courses, badges, adoption
- **Organizational Changes**: Model restructuring as part of rollout

Bridge modules (auto-installed when dependencies present):
- rollout_bpm: BPMN process engine integration
- rollout_mgmtsystem: ISO management system integration
- rollout_dashboard: BI dashboards via dashboard_vrtl
- rollout_gamification: Gamification badges, challenges, leaderboards
- rollout_lms: eLearning course integration

Dependencies (core): base, mail
License: AGPL-3
    """,
    'author': 'Vertel Sverige AB',
    'website': 'https://vertel.se',
    'license': 'AGPL-3',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'security/rollout_security.xml',
        'data/review_criteria_data.xml',
        'data/rollout_demo.xml',
        'views/rollout_project_views.xml',
        'views/rollout_phase_views.xml',
        'views/rollout_task_views.xml',
        'views/rollout_role_views.xml',
        'views/rollout_risk_views.xml',
        'views/rollout_scenario_views.xml',
        'views/rollout_sentiment_views.xml',
        'views/rollout_nudge_views.xml',
        'views/rollout_org_change_views.xml',
        'views/rollout_competency_target_views.xml',
        'views/rollout_competency_strategy_views.xml',
        'views/rollout_competency_scenario_views.xml',
        'views/rollout_plan_review_views.xml',
        'views/rollout_plan_review_criterion_views.xml',
        'views/rollout_menus.xml',
    ],
    'demo': [],
    'application': True,
    'installable': True,
    'auto_install': False,
}
