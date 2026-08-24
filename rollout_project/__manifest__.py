{
    "name": "Rollout Project Bridge",
    "version": "18.0.1.1.0",
    "category": "Project",
    "summary": "Bridge between rollout.project and project.project for timesheet, Gantt, budget",
    "depends": ["rollout", "project"],
    "data": [
        "security/ir.model.access.csv",
        "views/rollout_project_views.xml",
    ],
    "installable": True,
    "auto_install": True,
    "license": "LGPL-3",
}
