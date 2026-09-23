import { useState, Component } from "@odoo/owl";

export class Counter extends Component {
    static template = "awesome_owl.counter.counter";
    static props = ["callback"];

    setup() {
        this.state = useState({ value: 0 });
    }

    increment() {
        this.state.value++;
        this.props.callback();
    }
}
