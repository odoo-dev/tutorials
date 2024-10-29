import { registry } from "@web/core/registry";
import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";


class ClientAction extends Component {
    static template = "awesome_clicker.client_action";

    setup() {
        this.clickerService = useService("awesome_clicker.clicker_service");
        this.state = useState(this.clickerService.state);
    }

    increment10() {
        this.clickerService.increment(9);
    }
}

registry.category("actions").add("awesome_clicker.client_action", ClientAction);