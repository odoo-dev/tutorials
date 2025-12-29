import { Component } from "@odoo/owl";

export class TodoItem extends Component {
  static template = "todo.playground";

  static props = {
    todo: {
      type: Object,
      shape: {
        id: Number,
        description: String,
        isCompleted: Boolean,
      },
    },
    onComplete: { type: Function },
    onDelete: { type: Function },
  };
}
