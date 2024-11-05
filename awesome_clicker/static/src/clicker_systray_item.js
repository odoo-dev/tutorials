import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { useClicker } from "./useclicker"
import { ClickValue } from "./click_value"
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";


export class ClickerSystrayItem extends Component {
    static template = "awesome_clicker.systray_item";
    static components = { ClickValue, Dropdown, DropdownItem };

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

    get totalTrees() {
        let sum = 0;
        for (const tree in this.clicker.trees) {
            sum += this.clicker.trees[tree].purchased;
        }
        return sum;
    }

    get totalFruits() {
        let sum = 0;
        for (const fruit in this.clicker.fruits) {
            sum += this.clicker.fruits[fruit];
        }
        return sum;
    }
}

registry.category("systray").add("awesome_clicker.systray_item", {
    Component: ClickerSystrayItem,
});
