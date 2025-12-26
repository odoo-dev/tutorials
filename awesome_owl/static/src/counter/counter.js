import { Component } from "@odoo/owl";

export class Counter extends Component {
  static template = "counter.playground";

  static props = {
    counter: {
      type: Object,
      shape: {
        id: Number,
        value: Number,
      },
    },
    onIncrement: { type: Function },
  };

  increment() {
    this.props?.onIncrement?.();
  }
}
