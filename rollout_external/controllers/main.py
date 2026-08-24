"""Migration API controller for rollout_external."""

import json
import secrets
import hashlib
from datetime import datetime, timedelta

from odoo import http, fields, _
from odoo.http import request


class RolloutMigrationController(http.Controller):

    @http.route('/rollout/migration/generate_key', type='json', auth='user')
    def generate_migration_key(self, project_id):
        """Generate a one-time API key for migrating a project.

        Returns a URL with the key that the customer admin can use to import.
        """
        project = request.env['rollout.project'].browse(project_id)
        if not project.exists():
            return {'error': 'Project not found'}

        # Generate one-time key valid for 24h
        token = secrets.token_urlsafe(32)
        expiry = datetime.now() + timedelta(hours=24)

        # Store key hash in project (not the raw key)
        key_hash = hashlib.sha256(token.encode()).hexdigest()
        project.write({
            'migration_state': 'migrated',
            'migrated_at': fields.Datetime.now(),
        })
        # Store hash in a config parameter for validation
        request.env['ir.config_parameter'].sudo().set_param(
            f'rollout.migration.key.{project.id}', json.dumps({
                'hash': key_hash,
                'expiry': expiry.isoformat(),
                'project_id': project.id,
            }))

        base_url = request.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        migration_url = (
            f'{base_url}/rollout/migration/export/{project.id}?token={token}')

        return {
            'migration_url': migration_url,
            'expires_at': expiry.isoformat(),
        }

    @http.route('/rollout/migration/export/<int:project_id>', type='json', auth='public')
    def export_project(self, project_id, token=None):
        """Export project data for migration. Validates the one-time token."""
        if not token:
            return {'error': 'Token required'}

        # Validate token
        config = request.env['ir.config_parameter'].sudo().get_param(
            f'rollout.migration.key.{project_id}')
        if not config:
            return {'error': 'Invalid or expired token'}

        key_data = json.loads(config)
        key_hash = hashlib.sha256(token.encode()).hexdigest()
        if key_hash != key_data['hash']:
            return {'error': 'Invalid token'}

        expiry = datetime.fromisoformat(key_data['expiry'])
        if datetime.now() > expiry:
            return {'error': 'Token expired'}

        # Token valid — serialize project
        project = request.env['rollout.project'].sudo().browse(project_id)
        if not project.exists():
            return {'error': 'Project not found'}

        data = project._get_migration_data()

        # Invalidate token after use
        request.env['ir.config_parameter'].sudo().set_param(
            f'rollout.migration.key.{project_id}', '{}')

        return data
