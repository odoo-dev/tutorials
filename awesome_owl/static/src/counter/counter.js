/** @odoo-module **/

import { Component, useState, xml } from "@odoo/owl";

export default class Counter extends Component {
    static props = ["onChange"]

    static template = xml`
        <div class="card d-inline-block m-2">
            <div class="card-body">
                <p>
                    Counter: <t t-esc="state.value"/>
                </p>
                <button class="btn btn-primary" t-on-click="increment">
                    Increment
                </button>
            </div>
        </div>`;

    setup() {
        this.state = useState({ value: 0 });
    }

    increment() {
        this.state.value++;
        this.props.onChange();
    }
}
