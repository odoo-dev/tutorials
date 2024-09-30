/** @odoo-module **/

import {registry} from "@web/core/registry";
import {Component, useState} from "@odoo/owl";
import {useService} from "@web/core/utils/hooks";

export class ClickerSystray extends Component {
    static template = "awesome_clicker.ClickerSystray";

    setup() {
        this.clickService = useState(useService("clicker_service"));
        this.action = useService("action");
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