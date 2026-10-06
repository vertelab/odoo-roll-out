{
    "name": "Rollout App Coin Bridge",
    "version": "18.0.1.0.0",
    "category": "Project",
    "summary": "Credit coins when a rollout app line is completed",
    "description": """
Rollout App Coin Bridge
=======================

Pays coins into ``gamification_coin`` when a rollout app line is completed.

The app records ``coins_earned`` on the line; this bridge gives that number
a destination. It is the counterpart of ``rollout_app_gamification``, which
does the same for points and karma:

    rollout.app.line.done
          |
          +-- rollout_app_gamification --> _add_karma(points_earned)
          |
          +-- rollout_app_coin ----------> _add_coins(coins_earned)

Two bridges, two currencies, one completion event. The currency module stays
independent: it knows only that someone credited coins and where from. This
bridge knows nothing about the shop.
""",
    "author": "Vertel AB",
    "website": "https://vertel.se/apps/odoo-roll-out/rollout_app_coin",
    "license": "LGPL-3",
    "depends": ["rollout_app", "gamification_coin"],
    "data": [],
    "installable": True,
    "auto_install": True,
}
