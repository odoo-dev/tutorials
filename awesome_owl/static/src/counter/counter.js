import { Component, signal } from "@odoo/owl";

export class Counter extends Component {
    static template = "tutorial.counter";

    counter = signal(0)

    increment_one() {
        this.counter.set(this.counter() + 1)
    }
    decrement_one() {
        this.counter.set(this.counter() - 1)
    }
    reset() {
        this.counter.set(0)
    }
}
