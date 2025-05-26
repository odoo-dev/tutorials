import { Component } from "@odoo/owl";
import { ClickValue } from "./clicker_game/components/click_value";
import { Notebook, Page } from "@web/core/notebook/notebook";
import { useClicker } from "./utils";
import { registry } from "@web/core/registry";

class MyClientAction extends Component {
    static template = "clicker_game.clientaction";
    static components = { ClickValue, Notebook, Page };

    setup() {
        super.setup();
        this.clicker = useClicker();
    }
}

registry.category("actions").add("awesome_clicker.client_action", MyClientAction);