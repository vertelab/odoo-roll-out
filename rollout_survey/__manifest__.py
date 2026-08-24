{
    "name": "Rollout - Survey Bridge (OBMS)",
    "version": "18.0.1.0.0",
    "category": "Project",
    "summary": "OBMS pulse surveys for rollout projects via the survey module",
    "description": """
Rollout Survey Bridge Module
============================

Connects the survey module to rollout for Key.se OBMS-style pulse
measurement (baseline -> target state):

- survey.survey gets rollout project / phase / dimension / wave / type fields
- Scale answers (1-5) become rollout.sentiment scores
- Text answers become sentiment comments
- A button generates idempotent sentiment entries from completed inputs
- Works with rollout_ai: comments are automatically AI-analyzed for hotspots

Fully optional - requires both rollout and survey.
""",
    "author": "Vertel AB",
    "website": "https://vertel.se",
    "depends": ["rollout", "survey"],
    "data": [
        "views/survey_survey_views.xml",
    ],
    "installable": True,
    "auto_install": True,
    "application": False,
    "license": "LGPL-3",
}
