/** @odoo-module **/

import { Component, useState } from "@odoo/owl";

export class Card extends Component {
    static template = "awesome_owl.card";

    setup() {
        this.state = useState({isOpen: true});
    }

    flipIsOpen() {
        this.state.isOpen = !this.state.isOpen; 
    }

    static props = {
        title: { type: String },
                slots: { type: Object },

    };
}
