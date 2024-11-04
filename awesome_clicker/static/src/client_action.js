import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";
import { useClicker } from "./useclicker"
import { ClickValue } from "./click_value"


class ClientAction extends Component {
    static template = "awesome_clicker.client_action";
    static components = { ClickValue };

    setup() {
        this.clicker = useClicker();
    }
}

registry.category("actions").add("awesome_clicker.client_action", ClientAction);