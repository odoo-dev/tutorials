/** @odoo-module **/

import {Component, useState} from "@odoo/owl";

export class Card extends Component {
    static props = {
        title: {type: String, optional: true, default: "Card Title"},
        slots: {type: Object, optional: true, validate: slots => "default" in slots}
    }

    static template = "awesome_owl.Card";

    setup() {
        this.state = useState({
            isOpen: true
        });
    }

    toggleContent() {
        this.state.isOpen = !this.state.isOpen;
    }
}