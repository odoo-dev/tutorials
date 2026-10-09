import { Component, useState } from "@odoo/owl";

export class Playground extends Component {
    static template = "awesome_owl.playground";

    setup() {
        this.counter = useState({ value: 0 });
    }

    increment() {
        this.counter.value++;
    }

    decrement() {
        this.counter.value--;
    }
}
