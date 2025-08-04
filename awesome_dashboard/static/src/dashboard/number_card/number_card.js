import { Component } from "@odoo/owl";

export class NumberCard extends Component {
    static template = "awesome_dashboard.NumberCard";

    static props = {
        title: { type: String },
        number: { type: Number },
        size: { type: Number, default: 1, optional: true },
    };
}
