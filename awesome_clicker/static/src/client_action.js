import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";
import { useClicker } from "./useclicker"
import { ClickValue } from "./click_value"
import { Notebook } from "@web/core/notebook/notebook";


class ClientAction extends Component {
    static template = "awesome_clicker.client_action";
    static components = { ClickValue, Notebook };

    setup() {
        this.clicker = useClicker();
    }
}

registry.category("actions").add("awesome_clicker.client_action", ClientAction);