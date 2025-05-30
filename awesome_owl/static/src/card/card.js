import { Component, useState } from "@odoo/owl";

export class Card extends Component {
  static template = "awesome_owl.card";

  static props = {
    title: { type: String },
    number: { type: Number, optional: true },
    slots: {
      type: Object,
      shape: {
        default: true,
      },
    },
  };
  setup() {
    this.isOpen = useState({ value: false });
  }

  changeState() {
    this.isOpen.value = !this.isOpen.value;
  }
}
