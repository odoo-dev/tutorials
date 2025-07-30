/** @odoo-module **/

import { Component, useState } from "@odoo/owl";

export class Card extends Component {
    static template = "awesome_owl.card";

    static props = {
        title: { type: String },
        slots: { type: Object },
    };

    setup() {
        this.showCard = useState({ value: true });
    }

    toggleCard() {
        console.log("toggling");
        this.showCard.value = !this.showCard.value;
    }
}
