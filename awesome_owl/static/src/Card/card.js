/** @odoo-module **/

import { Component, useState } from "@odoo/owl";

export class Card extends Component {
    static template = "awesome_owl.card";

    static props = {
        title: String,
        // content: String,
        slots: {
            type: Object,
            shape: {
                default: true
            },
        }
    }

    setup() {
        this.state = useState({
            cardOpen: true
        });
    }

    toggleFlatten() {
        console.log(this.props.title, this.state.cardOpen)
        this.state.cardOpen = !this.state.cardOpen;
    }
}
