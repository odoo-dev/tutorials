import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";

class ClickerSystray extends Component {
    static template = "awesome_clicker.ClickerSystray";
    static props = {};

    setup() {
        this.state = useState({ counter: 0 });
    }

    increment() {
        this.state.counter++;
    }
}

export const systrayItem = {
        Component: ClickerSystray,
};

registry.category("systray").add("awesome_clicker.ClickerSystray", systrayItem, { sequence: 1000 });
