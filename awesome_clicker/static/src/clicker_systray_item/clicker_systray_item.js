/** @odoo-module **/

import {registry} from "@web/core/registry";
import {Component, useExternalListener, useState} from "@odoo/owl";
import {useService} from "@web/core/utils/hooks";

export class ClickerSystray extends Component {
    static template = "awesome_clicker.ClickerSystray";

    setup() {
        this.state = useState({count: 0});
        this.action = useService("action");
        useExternalListener(document.body, "click", () => this.state.count++, true);

    }

    increment() {
        this.state.count += 9;
    }

    openClickAction() {
        this.action.doAction({
            type: "ir.actions.client",
            tag: "awesome_clicker.client_action",
            target: "new",
            name: "Clicker"
        });
    }
}

export const systrayItem = {
    Component: ClickerSystray,
};

registry.category("systray").add("awesome_clicker.ClickerSystray", systrayItem, {sequence: 100});