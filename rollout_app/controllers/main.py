# -*- coding: utf-8 -*-
# Part of Vertel. See LICENSE file for full copyright and licensing details.

import os

from odoo import http
from odoo.modules.module import get_module_resource
from odoo.http import request


class RolloutAppController(http.Controller):
    """PWA endpoints: manifest, service worker and push subscriptions."""

    @http.route('/rollout_app/manifest.json', type='http', auth='user',
                methods=['GET'])
    def manifest(self, **kwargs):
        """Serve the web app manifest from the same origin as Odoo.

        Same origin is a hard requirement for Web Push, which is why this is
        served by Odoo rather than from a separate host.
        """
        manifest = {
            'name': 'My Rollout',
            'short_name': 'Rollout',
            'description': 'Personal action menu for Odoo rollouts',
            'start_url': '/odoo',
            'scope': '/',
            'display': 'standalone',
            'background_color': '#ffffff',
            'theme_color': '#714B67',
            'icons': [
                {
                    'src': '/rollout_app/static/description/icon-192.png',
                    'sizes': '192x192',
                    'type': 'image/png',
                },
                {
                    'src': '/rollout_app/static/description/icon-512.png',
                    'sizes': '512x512',
                    'type': 'image/png',
                },
            ],
        }
        return request.make_json_response(manifest)

    @http.route('/rollout_app/service-worker.js', type='http', auth='public',
                methods=['GET'])
    def service_worker(self, **kwargs):
        """Serve the service worker from the root scope.

        A service worker may only control pages at or below its own path, so
        serving it from ``/rollout_app/`` would not let it handle pushes for
        the Odoo backend. The ``Service-Worker-Allowed`` header widens the
        scope to ``/``.
        """
        path = get_module_resource(
            'rollout_app', 'static', 'src', 'js', 'service_worker.js')
        if not path or not os.path.exists(path):
            return request.not_found()
        with open(path, 'rb') as handle:
            body = handle.read()
        response = request.make_response(
            body, [('Content-Type', 'application/javascript')])
        response.headers['Service-Worker-Allowed'] = '/'
        response.headers['Cache-Control'] = 'no-cache'
        return response

    @http.route('/rollout_app/subscribe', type='json', auth='user',
                methods=['POST'])
    def subscribe(self, endpoint=None, keys=None, user_agent=None, **kwargs):
        """Store a push subscription for the current user."""
        if not endpoint or not keys:
            return {'ok': False, 'error': 'missing endpoint or keys'}
        Subscription = request.env['rollout.push.subscription'].sudo()
        existing = Subscription.search([('endpoint', '=', endpoint)], limit=1)
        values = {
            'user_id': request.env.user.id,
            'endpoint': endpoint,
            'p256dh': keys.get('p256dh'),
            'auth': keys.get('auth'),
            'user_agent': user_agent,
            'active': True,
        }
        if existing:
            existing.write(values)
        else:
            Subscription.create(values)
        return {'ok': True}

    @http.route('/rollout_app/unsubscribe', type='json', auth='user',
                methods=['POST'])
    def unsubscribe(self, endpoint=None, **kwargs):
        """Deactivate a push subscription."""
        if not endpoint:
            return {'ok': False, 'error': 'missing endpoint'}
        subscription = request.env['rollout.push.subscription'].sudo().search([
            ('endpoint', '=', endpoint),
            ('user_id', '=', request.env.user.id),
        ], limit=1)
        if subscription:
            subscription.active = False
        return {'ok': True}

    @http.route('/rollout_app/vapid_public_key', type='json', auth='user',
                methods=['POST'])
    def vapid_public_key(self, **kwargs):
        """The VAPID public key, needed by the browser to subscribe."""
        key = request.env['ir.config_parameter'].sudo().get_param(
            'rollout_app.vapid_public_key', '')
        return {'key': key}
