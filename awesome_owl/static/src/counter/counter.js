import { Component, useState } from "@odoo/owl";

export class Counter extends Component {
    static template = "awesome_owl.Counter";
    static props = {
        onChangeIncre: { type: Function, optional: true },
        onChangeDecre: { type: Function, optional: true },
    };

    setup() {
        this.state = useState({ value: -1 });
    }

    increment() {
        this.state.value++;
        if (this.props.onChangeIncre) {
            this.props.onChangeIncre();
        }
    }

    decrement() {
        this.state.value--;
        if (this.props.onChangeDecre) {
            this.props.onChangeDecre();
        }
    }

}