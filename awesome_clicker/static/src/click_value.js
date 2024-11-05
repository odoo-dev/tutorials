import { Component } from "@odoo/owl";
import { humanNumber } from "@web/core/utils/numbers";
import { useClicker } from "./useclicker";


export class ClickValue extends Component {
    static template = "awesome_clicker.click_value";
    static props = {};

    setup() {
        this.clicker = useClicker();
    }

    get humanizedClicks() {
        return humanNumber(this.clicker.clicks, {
            decimals: 1,
        });
    }
}
