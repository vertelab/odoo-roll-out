{
    "name": "Rollout",
    "version": "18.0.1.1.0",
    "category": "Project",
    "summary": "Behavioral science-driven organizational change management for Odoo implementations",
    "description": """
Rollout Core Module
===================

Manages organizational change during Odoo implementation using
behavioral science principles:

- ADKAR phase modeling (Awareness → Desire → Knowledge → Ability → Reinforcement)
- Competency targets with automatic gap analysis
- Role definitions with skill, course, badge, and task requirements
- Behavioral nudging engine (template + trigger, standalone, no AI dependency)
- Sentiment pulse tracking
- Risk register with probability × impact scoring
- Organizational change tracking (new departments, restructures, reporting changes)
- What-if scenario analysis for timeline planning
- Multi-dimensional plan review (42 criteria across 9 dimensions)
- Portfolio management for multiple parallel rollout projects

Fully standalone — only depends on base and mail. All optional integrations
via bridge modules (rollout_project, rollout_gamification, rollout_recruitment,
rollout_hr_evaluation, rollout_ai).
""",
    "author": "Vertel AB",
    "website": "https://vertel.se",
    "depends": ["base", "mail", "hr"],
    "data": [
        "security/ir.model.access.csv",
        "views/rollout_project_views.xml",
        "views/rollout_phase_views.xml",
        "views/rollout_competency_target_views.xml",
        "views/rollout_role_views.xml",
        "views/rollout_sentiment_views.xml",
        "views/rollout_risk_views.xml",
        "views/rollout_org_change_views.xml",
        "views/rollout_scenario_views.xml",
        "views/rollout_plan_review_views.xml",
        "views/rollout_nudge_views.xml",
        "views/rollout_portfolio_views.xml",
        "views/menu_views.xml",
    ],
    "assets": {},
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "LGPL-3",
}
