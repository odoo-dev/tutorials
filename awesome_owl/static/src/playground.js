import { Component, markup, useState, xml } from "@odoo/owl";

export class Counter extends Component {
  static template = "awesome_owl.playground";

  setup() {
    this.state = useState({ value: 0 });
  }

  increment() {
    this.state.value += 1;
  }

  static props = {
    label: { type: String },
    content: { type: String }
  };
}

export class Playground extends Component {
  setup() {
    this.firstContent = markup('<span class="text-primary">First HTML content</span>');
    this.secondContent = markup('<strong class="text-success">Second HTML content</strong>');
  }

  static template = xml`
    <div class="p-3 d-flex flex-column align-items-center justify-content-center vh-100">
      <Counter label="'Counter: '" content="firstContent" />
      <Counter label="'Retnuoc: '" content="secondContent" />
    </div>
  `;

  static components = { Counter };
}
