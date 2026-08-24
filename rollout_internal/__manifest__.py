{
    "name": "Rollout Internal",
    "version": "18.0.1.0.0",
    "category": "Project",
    "summary": "Organizational change platform — employee journey for Odoo rollouts",
    "description": """
Rollout Internal Module
=======================

Organization's change platform installed in the customer's Odoo instance.
Provides the employee-facing change journey.

Features:
- Employee dashboard: personal competency targets, roles, nudges
- Full behavioral nudging engine with role and phase scoping
- Employee-facing views for personal progress tracking
- Nudge delivery via Odoo notifications
- Auto-activates bridge modules when HR dependencies are present:
  rollout_gamification (requires gamification)
  rollout_recruitment (requires hr_recruitment)
  rollout_hr_evaluation (requires hr_evaluation)
""",
    "author": "Vertel AB",
    "website": "https://vertel.se",
    "depends": ["rollout"],
    "data": [
        "security/ir.model.access.csv",
        "views/dashboard_views.xml",
        "views/employee_views.xml",
        "views/menu_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "LGPL-3",
}
