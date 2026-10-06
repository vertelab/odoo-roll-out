/** @odoo-module **/

/**
 * PWA and push registration for the Rollout app.
 *
 * Registers the service worker, subscribes to Web Push, and detects whether
 * the app is installed to the home screen (which some platforms require
 * before push works at all).
 */

import { registry } from "@web/core/registry";
import { browser } from "@web/core/browser/browser";

function urlBase64ToUint8Array(base64String) {
    const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
    const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");
    const raw = window.atob(base64);
    const output = new Uint8Array(raw.length);
    for (let i = 0; i < raw.length; ++i) {
        output[i] = raw.charCodeAt(i);
    }
    return output;
}

/** Whether the app is running installed (standalone) rather than in a tab. */
export function isStandalone() {
    return (
        window.matchMedia("(display-mode: standalone)").matches ||
        window.navigator.standalone === true
    );
}

/** Whether this looks like iOS, where push needs a home-screen install. */
export function isIos() {
    return /iPad|iPhone|iPod/.test(window.navigator.userAgent);
}

export const rolloutAppService = {
    dependencies: [],

    start() {
        // Register the service worker from the root scope.
        if ("serviceWorker" in navigator) {
            navigator.serviceWorker
                .register("/rollout_app/service-worker.js", { scope: "/" })
                .catch((err) => {
                    console.warn("rollout_app: service worker failed", err);
                });
        }
    },
};

registry.category("services").add("rollout_app", rolloutAppService);

/**
 * Subscribe the current browser to Web Push.
 *
 * Returns a result object rather than throwing, so the caller can show a
 * sensible message for each failure mode (no support, permission denied,
 * no VAPID key configured).
 */
export async function subscribeToPush(env) {
    if (!("serviceWorker" in navigator) || !("PushManager" in window)) {
        return { ok: false, reason: "unsupported" };
    }
    if (isIos() && !isStandalone()) {
        return { ok: false, reason: "ios-needs-install" };
    }

    const permission = await Notification.requestPermission();
    if (permission !== "granted") {
        return { ok: false, reason: "permission-denied" };
    }

    const { key } = await env.services.rpc("/rollout_app/vapid_public_key", {});
    if (!key) {
        return { ok: false, reason: "no-vapid-key" };
    }

    const registration = await navigator.serviceWorker.ready;
    const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(key),
    });

    const json = subscription.toJSON();
    await env.services.rpc("/rollout_app/subscribe", {
        endpoint: json.endpoint,
        keys: json.keys,
        user_agent: window.navigator.userAgent,
    });
    return { ok: true };
}
