import { registry } from "@web/core/registry";
import { Component, useState, useExternalListener } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";


export class ClickerSystrayItem extends Component {
    static template = "awesome_clicker.systray_item";

    setup() {
        useExternalListener(window, "click", this.increment, { capture: true });
        this.clickerGameAction = useService("action");
        this.clickerService = useService("awesome_clicker.clicker_service");
        this.state = useState(this.clickerService.state);
    }

    increment() {
        this.clickerService.increment(1);
    }

    increment10() {
        this.clickerService.increment(9);
    }

    openClickerGame() {
        this.clickerGameAction.doAction({
            type: "ir.actions.client",
            tag: "awesome_clicker.client_action",
            target: "new",
            name: "Clicker"
         });
    }
}

registry.category("systray").add("awesome_clicker.systray_item", {
    Component: ClickerSystrayItem,
});
