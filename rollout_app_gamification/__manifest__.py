{
    "name": "Rollout App Gamification Bridge",
    "version": "18.0.1.0.0",
    "category": "Project",
    "summary": "Award karma for completed app lines, and unlock gated content",
    "description": """
Rollout App Gamification Bridge
===============================

Connects the app's participant lines to Odoo's gamification.

The app is a consumer: gamification owns karma and badges, and this bridge
only reports completions to it. Two things happen when a line is completed:

* karma is awarded via ``res.users._add_karma``, once per line;
* a locked advanced line gated on that line is unlocked for that person.

Badges are never created here. ``rollout.module.line.badge_id`` is a display
link only.
""",
    "author": "Vertel Sverige AB",
    "website": "https://vertel.se/apps/odoo-roll-out/rollout_app_gamification",
    "license": "LGPL-3",
    "depends": ["rollout_app", "gamification"],
    "data": [],
    "installable": True,
    "auto_install": True,
}
