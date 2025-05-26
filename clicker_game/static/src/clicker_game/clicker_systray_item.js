import { registry } from "@web/core/registry";
import { useClicker } from "../utils"
import { useService } from "@web/core/utils/hooks";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { Component, useExternalListener } from "@odoo/owl";
import { ClickValue } from "./components/click_value";

const clickerMenuRegistry = registry.category("clicker_menuitems");

export class ClickerGame extends Component {
    static template = "clicker_game.count";
    static props = {};
    static components = { ClickValue, Dropdown, DropdownItem };

    setup() {
        super.setup();
        this.clicker = useClicker();
        this.action = useService("action");
        useExternalListener(window, "click", this.clicker.increment, true);
    }

    open(){
        this.action.doAction({
            type: "ir.actions.client",
            tag: "awesome_clicker.client_action",
            target: "new",
            name: "Clicker Game"
        });
    }

    getElements() {
        const sortedItems = clickerMenuRegistry
            .getAll()
            .map((element) => element(this.env))
            .sort((x, y) => {
                const xSeq = x.sequence ? x.sequence : 100;
                const ySeq = y.sequence ? y.sequence : 100;
                return xSeq - ySeq;
            });
        return sortedItems;
    }

    trigger(item) {
        if (item.type === "function") {
            if(item.id === "open") {
                this.open();
            }   
            else if (item.id === "buyClickBot" && this.clicker.clicks.count >= 1000) {
                this.clicker.buyClickBot();
            }
        }
        else {
            return;
        }
    }

    getValue(item) {
        if(item.type!="function") {
            const str = item.id;
            return this.clicker[str];
        }
    }
}

export const systrayItem = {
    Component: ClickerGame,
};
registry.category("systray").add("web.clicker_game", systrayItem, { sequence: 150 });
