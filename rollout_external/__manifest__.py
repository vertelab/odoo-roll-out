{
    "name": "Rollout External",
    "version": "18.0.1.1.0",
    "category": "Project",
    "summary": "Consultant tooling for managing Odoo rollouts from outside the organization",
    "description": """
Rollout External Module
=======================

Consultant's toolbox for driving Odoo rollout implementations from an external
perspective. Installed in the consultant's Odoo instance.

Features:
- Portfolio dashboard with metrics across all customer projects
- Consultant-specific views: recommendations, customer reports, internal notes
- Scenario comparison for offer preparation
- Migration API for transferring projects to customer instances
- Auto-activates rollout_project bridge for timesheet/Gantt integration
""",
    "author": "Vertel AB",
    "website": "https://vertel.se",
    "depends": ["rollout"],
    "data": [
        "security/ir.model.access.csv",
        "views/dashboard_views.xml",
        "views/consultant_views.xml",
        "views/menu_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "LGPL-3",
}
