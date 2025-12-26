import { Component } from "@odoo/owl";

export class Card extends Component {
  static template = "card.playground";

  static props = {
    title: {
      type: String,
    },
    content: { type: String | Number },
  };
}
