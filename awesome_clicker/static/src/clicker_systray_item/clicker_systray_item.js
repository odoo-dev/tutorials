import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class ClickerSystray extends Component {
    static template = "awesome_clicker.ClickerSystray";
    static props = {};

    setup() {
        this.clickerService = useState(useService("awesome_clicker.clicker"));
        this.action = useService("action");
    }

    openClientAction() {
        this.action.doAction({
            type: "ir.actions.client",
            tag: "awesome_clicker.client_action",
            target: "new",
            name: "Clicker",
        });
    }
}

export const systrayItem = {
        Component: ClickerSystray,
};

registry.category("systray").add("awesome_clicker.ClickerSystray", systrayItem, { sequence: 1000 });
