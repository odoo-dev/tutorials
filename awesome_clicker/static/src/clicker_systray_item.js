import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { useClicker } from "./useclicker"
import { ClickValue } from "./click_value"


export class ClickerSystrayItem extends Component {
    static template = "awesome_clicker.systray_item";
    static components = { ClickValue };

    setup() {
        this.clickerGameAction = useService("action");
        this.clicker = useClicker();
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
