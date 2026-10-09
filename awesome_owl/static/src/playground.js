import { Component, useState, xml } from "@odoo/owl";

export class Counter extends Component {
  static template = "awesome_owl.playground";

  setup() {
    this.state = useState({ value: 0 });
  }

  increment() {
    this.state.value += 1;
  }
}

export class Playground extends Component {
  static template = xml`
    <div class="p-3 d-flex flex-column align-items-center justify-content-center vh-100">
      <Counter />
      <Counter />
    </div>
  `

  static components = { Counter };
}
