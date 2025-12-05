import { Component, useState } from "@odoo/owl"

export class Card extends Component {
    static props = {
        title: {type: String},
        content: {type: String, optional: true},
        slots: {type: Object, optional: true}
    };
    static template = "awesome_owl.card";
}