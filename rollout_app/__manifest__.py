{
    "name": "Rollout App",
    "version": "18.0.1.0.0",
    "category": "Project",
    "summary": "Personal action menu and points loop for Odoo rollouts",
    "description": """
Rollout App
===========

The daily entry point for a rollout participant: a short, personal menu of
things to do, points for doing them, and a weekly rhythm.

Where ``rollout_internal`` shows plain lists, this module provides the loop:
action → points → recognition. It is a consumer of ``gamification``, never a
modifier — badges and karma are owned by Odoo's gamification module.

Three models, no template level:

* ``rollout.module``      — a content type (course, survey, referral)
* ``rollout.module_line`` — an instance of that type
* ``rollout.app.line``    — one person's outcome for one line

Plus ``rollout.app`` — the project's menu.

Two spawn modes: ``static`` (a course list, constant, waits until done) and
``periodic`` (a survey, spawned each period and retired when the period ends).

Two openers: time (``publish_at``) and achievement (a locked advanced course
opened by gamification).

Also provides a PWA shell (manifest, service worker) and Web Push delivery.
""",
    "author": "Vertel Sverige AB",
    "website": "https://vertel.se/apps/odoo-roll-out/rollout_app",
    "license": "LGPL-3",
    "depends": ["rollout", "rollout_internal", "web"],
    "external_dependencies": {
        "python": ["pywebpush"],
    },
    "data": [
        "security/rollout_app_security.xml",
        "security/ir.model.access.csv",
        "views/rollout_module_views.xml",
        "views/rollout_app_views.xml",
        "views/rollout_app_line_views.xml",
        "views/rollout_push_subscription_views.xml",
        "views/rollout_app_menus.xml",
        "views/rollout_internal_override.xml",
        "data/ir_cron_data.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "rollout_app/static/src/js/rollout_app_push.js",
            "rollout_app/static/src/js/rollout_app_prompt.js",
            "rollout_app/static/src/xml/rollout_app_templates.xml",
        ],
    },
    "post_init_hook": "post_init_hook",
    "installable": True,
    "application": True,
    "auto_install": False,
}
