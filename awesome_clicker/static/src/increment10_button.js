import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";


export class Increment10Button extends Component {
    static template = "awesome_clicker.increment10_button";

    setup() {
        this.clickerService = useService("awesome_clicker.clicker_service");
        this.state = useState(this.clickerService.state);
    }

    increment10() {
        this.clickerService.increment(9);
    }
}
