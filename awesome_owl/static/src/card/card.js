import { Component, markup, useState } from "@odoo/owl";

export class Card extends Component {
    static template = "awesome_owl.Card";
    static props = {
        title: String,
        content: {
            type: String,
            optional: true,
        },
        slots: {
            type: Object,
        }
    };

    setup() {
        // this.htmltest= markup("<div class='text-primary'>some content3</div>");
        // this.props.content = this.htmltest;
    }
}