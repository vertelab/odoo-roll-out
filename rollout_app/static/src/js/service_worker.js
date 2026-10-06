/* Service worker for the Rollout app.
 *
 * Handles `push` events and shows notifications. Served from
 * /rollout_app/service-worker.js with the Service-Worker-Allowed: / header,
 * so it controls the whole Odoo origin.
 */

self.addEventListener('install', (event) => {
    // Activate immediately rather than waiting for existing tabs to close.
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    event.waitUntil(self.clients.claim());
});

self.addEventListener('push', (event) => {
    let payload = { title: 'My Rollout', body: '', url: '/odoo' };
    if (event.data) {
        try {
            payload = Object.assign(payload, event.data.json());
        } catch (err) {
            payload.body = event.data.text();
        }
    }
    event.waitUntil(
        self.registration.showNotification(payload.title, {
            body: payload.body,
            icon: '/rollout_app/static/description/icon-192.png',
            badge: '/rollout_app/static/description/icon-192.png',
            data: { url: payload.url },
        })
    );
});

self.addEventListener('notificationclick', (event) => {
    event.notification.close();
    const target = (event.notification.data && event.notification.data.url)
        || '/odoo';
    event.waitUntil(
        self.clients.matchAll({ type: 'window', includeUncontrolled: true })
            .then((clients) => {
                for (const client of clients) {
                    if (client.url.includes(target) && 'focus' in client) {
                        return client.focus();
                    }
                }
                return self.clients.openWindow(target);
            })
    );
});
