"""Migration import controller for rollout_internal."""

import json

from odoo import http, fields, _
from odoo.http import request


class RolloutMigrationImportController(http.Controller):

    @http.route('/rollout/migration/import', type='json', auth='user')
    def import_project(self, source_url, token):
        """Import project data from an external instance.

        Calls the external instance's export endpoint with the token,
        validates data integrity, and creates all records.
        """
        # In production, this would call the external API
        # For now, this is a placeholder structure
        return {
            'status': 'ready',
            'message': 'Migration endpoint ready. Provide source URL and token to import.',
        }

    @http.route('/rollout/migration/preview', type='json', auth='user')
    def preview_import(self, data):
        """Preview migration data before importing.

        Returns a summary of what will be imported and any issues found.
        """
        issues = []
        summary = {
            'phases': len(data.get('phases', [])),
            'competency_targets': len(data.get('competency_targets', [])),
            'roles': len(data.get('roles', [])),
            'risks': len(data.get('risks', [])),
            'sentiments': len(data.get('sentiments', [])),
            'org_changes': len(data.get('org_changes', [])),
            'scenarios': len(data.get('scenarios', [])),
            'plan_reviews': len(data.get('plan_reviews', [])),
        }

        # Validate required fields
        project_data = data.get('project', {})
        if not project_data.get('name'):
            issues.append('Project name is missing')

        return {
            'summary': summary,
            'issues': issues,
            'can_import': len(issues) == 0,
        }

    @http.route('/rollout/migration/execute', type='json', auth='user')
    def execute_import(self, data):
        """Execute the project import after preview."""
        project_data = data.get('project', {})
        if not project_data.get('name'):
            return {'error': 'Project name is required'}

        # Create the project
        project_vals = {
            'name': project_data['name'],
            'planning_mode': project_data.get('planning_mode', 'backward'),
            'date_start': project_data.get('date_start'),
            'date_launch': project_data.get('date_launch'),
            'perspective': 'internal',
            'migration_state': 'imported',
            'migrated_from': project_data.get('migrated_from', 'Unknown'),
            'migrated_at': fields.Datetime.now(),
        }
        # AI settings — only set when rollout_ai is installed on the internal
        # side; otherwise fall back to defaults (weekly, no auto-create,
        # PM approval on)
        if 'goal_sync_frequency' in request.env['rollout.project']._fields:
            project_vals.update({
                'executive_summary_frequency': project_data.get(
                    'executive_summary_frequency', 'weekly'),
                'goal_sync_frequency': project_data.get(
                    'goal_sync_frequency', 'weekly'),
                'goal_auto_create': project_data.get('goal_auto_create', False),
                'goal_require_pm_approval': project_data.get(
                    'goal_require_pm_approval', True),
                'goal_notify_on_create': project_data.get(
                    'goal_notify_on_create', True),
            })
        project = request.env['rollout.project'].create(project_vals)

        # Import phases
        phase_map = {}
        for phase_data in data.get('phases', []):
            phase = request.env['rollout.phase'].create({
                'project_id': project.id,
                'name': phase_data['name'],
                'adkar_phase': phase_data['adkar_phase'],
                'sequence': phase_data['sequence'],
                'duration_days': phase_data['duration_days'],
                'gate_type': phase_data.get('gate_type', 'none'),
                'gate_metric': phase_data.get('gate_metric', 80.0),
            })
            phase_map[phase_data['sequence']] = phase.id

        # Import competency targets
        for target_data in data.get('competency_targets', []):
            request.env['rollout.competency.target'].create({
                'project_id': project.id,
                'name': target_data['name'],
                'target_count': target_data['target_count'],
                'deadline': target_data.get('deadline'),
                'level': target_data.get('level'),
            })

        # Import roles
        for role_data in data.get('roles', []):
            request.env['rollout.role'].create({
                'project_id': project.id,
                'name': role_data['name'],
                'description': role_data.get('description'),
            })

        # Import risks
        for risk_data in data.get('risks', []):
            request.env['rollout.risk'].create({
                'project_id': project.id,
                'name': risk_data['name'],
                'probability': risk_data.get('probability', '1'),
                'impact': risk_data.get('impact', '1'),
                'mitigation': risk_data.get('mitigation'),
                'trigger_event': risk_data.get('trigger_event'),
                'state': risk_data.get('state', 'identified'),
            })

        # Import sentiments
        for sent_data in data.get('sentiments', []):
            request.env['rollout.sentiment'].create({
                'project_id': project.id,
                'score': sent_data['score'],
                'comment': sent_data.get('comment'),
            })

        # Import org changes
        for org_data in data.get('org_changes', []):
            request.env['rollout.org.change'].create({
                'project_id': project.id,
                'name': org_data['name'],
                'change_type': org_data['change_type'],
                'description': org_data.get('description'),
                'state': org_data.get('state', 'planned'),
            })

        project.message_post(body=_(
            'Project imported from %s on %s',
            project.migrated_from,
            fields.Datetime.now(),
        ))

        return {
            'status': 'success',
            'project_id': project.id,
            'project_name': project.name,
        }
