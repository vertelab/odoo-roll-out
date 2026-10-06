/** @odoo-module **/

/**
 * Install guidance and push opt-in for the Rollout app.
 *
 * Shown as a small banner. The message depends on why push is not available:
 *
 * * iOS in a browser tab — Web Push requires the app to be installed to the
 *   home screen first, so the banner explains that rather than offering a
 *   button that would fail;
 * * unsupported browser — nothing to offer;
 * * otherwise — an "Enable" button that subscribes.
 *
 * The banner is dismissed for the session, not permanently, so a user who
 * said "later" is asked again next time rather than never.
 */

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { isIos, isStandalone, subscribeToPush } from "./rollout_app_push";

const DISMISS_KEY = "rollout_app.push_prompt_dismissed";

export class RolloutAppPushPrompt extends Component {
    static template = "rollout_app.PushPrompt";
    static props = {};

    setup() {
        this.notification = useService("notification");
        this.state = useState({
            show: false,
            message: "",
            action: null,
        });

        onWillStart(async () => {
            await this._decide();
        });
    }

    async _decide() {
        // Already installed and permitted: nothing to say.
        if (sessionStorage.getItem(DISMISS_KEY)) {
            return;
        }
        if (!("Notification" in window)) {
            return;
        }
        if (Notification.permission === "granted") {
            return;
        }

        if (isIos() && !isStandalone()) {
            // The iOS case: push needs a home-screen install. Explain it
            // rather than offering a button that cannot work.
            this.state.show = true;
            this.state.message =
                "För att få notiser på iPhone: tryck på Dela och välj " +
                "Lägg till på hemskärmen. Öppna sedan appen därifrån.";
            this.state.action = "ios";
            return;
        }

        if (!("serviceWorker" in navigator) || !("PushManager" in window)) {
            return;
        }

        this.state.show = true;
        this.state.message = "Få en påminnelse när nya uppgifter publiceras.";
        this.state.action = "enable";
    }

    async onEnable() {
        const result = await subscribeToPush(this.env);
        if (result.ok) {
            this.notification.add("Notiser aktiverade.", { type: "success" });
            this.state.show = false;
        } else if (result.reason === "ios-needs-install") {
            this.state.message =
                "Lägg till appen på hemskärmen först — sedan kan du " +
                "aktivera notiser.";
        } else if (result.reason === "permission-denied") {
            this.notification.add(
                "Notiser nekades. Du kan ändra det i webbläsarens " +
                "inställningar.",
                { type: "warning" }
            );
            this.state.show = false;
        } else if (result.reason === "no-vapid-key") {
            this.notification.add(
                "Notiser är inte konfigurerade på servern.", { type: "warning" }
            );
            this.state.show = false;
        }
    }

    onDismiss() {
        sessionStorage.setItem(DISMISS_KEY, "1");
        this.state.show = false;
    }
}

registry.category("main_components").add("rollout_app.PushPrompt", {
    Component: RolloutAppPushPrompt,
});
