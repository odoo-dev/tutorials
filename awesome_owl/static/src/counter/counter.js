/** @odoo-module **/

import {Component, useState} from "@odoo/owl";

export class Counter extends Component {
    static props = {
        onChange: {type: Function, optional: true},
    };
    static template = "awesome_owl.Counter";

    setup() {
        this.state = useState({count: 1});
    }

    increment() {
        this.state.count++;
        if (this.props.onChange) {
            this.props.onChange(this.state.count);
        }
    }
}
