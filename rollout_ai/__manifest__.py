{
    "name": "Rollout AI",
    "version": "18.0.1.1.0",
    "category": "Project",
    "summary": "AI-powered bridge between rollout and odoo-mind — executive summaries, graph, goal sync, nudge upgrade",
    "description": """
Rollout AI Bridge Module
========================

Connects rollout projects to odoo-mind (ai_agent_core) for AI-powered features:

- Weekly AI-generated executive summaries per rollout project
- Apache AGE graph integration — rollout models as graph nodes with Cypher querying
- ai.personal.goal sync — competency targets create SMART goals, two-way status sync
- AI sentiment analysis — LLM hotspot detection from free-text comments
- AI plan review — LLM-assisted scoring of 42 criteria
- Nudge upgrade — odoo-mind delivery channels (mail.activity, calendar, email)
  3-level measurement (exposure → action → outcome), anti-spam thresholds

Fully optional — rollout works fine without this module. Requires ai_agent_core
with Apache AGE and pgvector installed.
""",
    "author": "Vertel AB",
    "website": "https://vertel.se",
    "depends": ["rollout", "ai_agent_core"],
    "data": [
        "security/ir.model.access.csv",
        "data/graph_definitions.xml",
        "data/cron_sync_graph.xml",
        "views/summary_views.xml",
        "views/goal_sync_views.xml",
        "views/sentiment_views.xml",
        "views/plan_review_views.xml",
        "views/nudge_views.xml",
    ],
    "installable": True,
    "auto_install": True,
    "license": "LGPL-3",
    "post_init_hook": "_post_init_rollout_graph",
}
