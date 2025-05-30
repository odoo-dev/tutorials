import { Component, useState } from "@odoo/owl";

export class TodoItem extends Component {
    static template = "awesome_owl.todo_item";

    static props = {
        id: {type: Number},
        description: { type: String},
        onDelete:Function
    };

    setup() {
        this.isCompleted = useState({ value: false });
    }

    toggleState() {
        this.isCompleted.value = !this.isCompleted.value
    }
}
