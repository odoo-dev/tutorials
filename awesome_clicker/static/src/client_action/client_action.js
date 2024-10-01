/** @odoo-module **/

import {registry} from "@web/core/registry";
import {Component} from "@odoo/owl";
import {useClicker} from "../clicker_hook";

export class ClientAction extends Component {
    static template = "awesome_clicker.ClientAction";

    setup() {
        this.clicker = useClicker();
    }

}

registry.category("actions").add("awesome_clicker.client_action", ClientAction);

