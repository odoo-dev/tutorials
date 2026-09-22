import { Component, useState, xml } from "@odoo/owl";

export class Counter extends Component {
    static template = xml` <button t-on-click="increment"> Click Me! [<t t-esc="state.value"/>] </button>`;

    setup() {
        this.state = useState({ value: 0 });
    }
    
    increment() {
        this.state.value++;
    }
}