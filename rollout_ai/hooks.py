"""Post-install hooks for rollout_ai — bulk index rollout models into AGE graph."""

import logging

_logger = logging.getLogger(__name__)


def _post_init_rollout_graph(env):
    """Bulk index existing rollout records into the odoo_mind graph.

    Called once when rollout_ai is installed. Uses ai_agent_core's
    graph_executor to create nodes and edges for all existing rollout data.
    """
    _logger.info("rollout_ai: Starting post_init graph indexing...")

    # Verify AGE is available
    # NOTE: wrapped in a savepoint — a permission failure (e.g. the app role
    # lacking SELECT on ag_catalog.ag_graph) must not poison the install
    # transaction ("current transaction is aborted" would kill all later
    # data loads).
    try:
        with env.cr.savepoint():
            env.cr.execute(
                "SELECT * FROM ag_catalog.ag_graph WHERE name = 'odoo_mind'")
            if not env.cr.fetchone():
                _logger.warning(
                    "rollout_ai: odoo_mind graph not found. "
                    "Skipping graph indexing. Install AGE first.")
                return
    except Exception as e:
        _logger.warning("rollout_ai: AGE not available: %s", e)
        return

    graph = env['graph.executor']
    batch_size = 500

    # Index rollout.projects
    projects = env['rollout.project'].search([], limit=5000)
    _logger.info("rollout_ai: Indexing %d projects...", len(projects))
    for i in range(0, len(projects), batch_size):
        batch = projects[i:i + batch_size]
        graph.bulk_upsert_nodes('RolloutProject', batch, {
            'name': 'name',
            'state': 'state',
            'perspective': 'perspective',
            'progress': 'overall_progress',
            'risk_score': 'total_risk_score',
        })

    # Index rollout.phases
    phases = env['rollout.phase'].search([], limit=10000)
    _logger.info("rollout_ai: Indexing %d phases...", len(phases))
    for i in range(0, len(phases), batch_size):
        batch = phases[i:i + batch_size]
        graph.bulk_upsert_nodes('RolloutPhase', batch, {
            'name': 'name',
            'adkar_phase': 'adkar_phase',
            'gate_type': 'gate_type',
            'gate_passed': 'gate_passed',
            'progress': 'progress',
        })
        # Create edges: HAS_PHASE (project → phase), PRECEDES (phase → phase)
        for phase in batch:
            if phase.project_id:
                graph.create_edge('RolloutProject', phase.project_id.id,
                                  'RolloutPhase', phase.id,
                                  'HAS_PHASE')
            if phase.preceding_phase_id:
                graph.create_edge('RolloutPhase', phase.preceding_phase_id.id,
                                  'RolloutPhase', phase.id,
                                  'PRECEDES')

    # Index competency targets
    targets = env['rollout.competency.target'].search([], limit=5000)
    _logger.info("rollout_ai: Indexing %d competency targets...", len(targets))
    for i in range(0, len(targets), batch_size):
        batch = targets[i:i + batch_size]
        graph.bulk_upsert_nodes('CompetencyTarget', batch, {
            'name': 'name',
            'target_count': 'target_count',
            'current_count': 'current_count',
            'gap': 'gap',
            'state': 'state',
        })
        for target in batch:
            if target.phase_id:
                graph.create_edge('RolloutPhase', target.phase_id.id,
                                  'CompetencyTarget', target.id,
                                  'HAS_COMPETENCY_TARGET')
            if target.role_id:
                graph.create_edge('CompetencyTarget', target.id,
                                  'RolloutRole', target.role_id.id,
                                  'TARGETS_ROLE')

    # Index roles
    roles = env['rollout.role'].search([], limit=1000)
    _logger.info("rollout_ai: Indexing %d roles...", len(roles))
    for i in range(0, len(roles), batch_size):
        batch = roles[i:i + batch_size]
        graph.bulk_upsert_nodes('RolloutRole', batch, {
            'name': 'name',
        })

    # Index risks
    risks = env['rollout.risk'].search([], limit=5000)
    _logger.info("rollout_ai: Indexing %d risks...", len(risks))
    for i in range(0, len(risks), batch_size):
        batch = risks[i:i + batch_size]
        graph.bulk_upsert_nodes('RolloutRisk', batch, {
            'name': 'name',
            'risk_score': 'risk_score',
            'state': 'state',
        })
        for risk in batch:
            if risk.project_id:
                graph.create_edge('RolloutProject', risk.project_id.id,
                                  'RolloutRisk', risk.id,
                                  'HAS_RISK')

    # Index sentiments
    sentiments = env['rollout.sentiment'].search([], limit=10000)
    _logger.info("rollout_ai: Indexing %d sentiment entries...", len(sentiments))
    for i in range(0, len(sentiments), batch_size):
        batch = sentiments[i:i + batch_size]
        graph.bulk_upsert_nodes('RolloutSentiment', batch, {
            'score': 'score',
        })
        for s in batch:
            if s.project_id:
                graph.create_edge('RolloutProject', s.project_id.id,
                                  'RolloutSentiment', s.id,
                                  'HAS_SENTIMENT')

    # Index org changes
    org_changes = env['rollout.org.change'].search([], limit=2000)
    _logger.info("rollout_ai: Indexing %d org changes...", len(org_changes))
    for i in range(0, len(org_changes), batch_size):
        batch = org_changes[i:i + batch_size]
        graph.bulk_upsert_nodes('RolloutOrgChange', batch, {
            'name': 'name',
            'change_type': 'change_type',
            'state': 'state',
        })
        for oc in batch:
            if oc.phase_id:
                graph.create_edge('RolloutPhase', oc.phase_id.id,
                                  'RolloutOrgChange', oc.id,
                                  'HAS_ORG_CHANGE')

    # Auto-enrich nudges
    nudges = env['rollout.nudge'].search([('enriched_by_ai', '=', False)])
    if nudges:
        _logger.info("rollout_ai: Enriching %d nudges...", len(nudges))
        nudges.write({'enriched_by_ai': True})

    _logger.info("rollout_ai: Graph indexing complete.")
