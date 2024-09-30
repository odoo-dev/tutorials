/** @odoo-module **/

import {registry} from "@web/core/registry";
import {Component, useState} from "@odoo/owl";
import {useService} from "@web/core/utils/hooks";

export class ClientAction extends Component {
    static template = "awesome_clicker.ClientAction";

    setup() {
        this.clickService = useState(useService("clicker_service"));
    }

}

registry.category("actions").add("awesome_clicker.client_action", ClientAction);

