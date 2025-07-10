/** @odoo-module **/

import { Component } from "@odoo/owl";

export class TodoItem extends Component {
    static template = "awesome_owl.todoitem";
    static props = {
        todo: {
            type: Object,
            shape: {
                id: Number,
                description: String,
                isCompleted: Boolean,
            }
        },
        toggleState: {
            type: Function,
        },
        removeTodoItem: {
            type: Function,
        }
    }

    removeTodoItem() {
        this.props.removeTodoItem(this.props.todo.id);
    }

    toggleTodoItem() {
        this.props.toggleState(this.props.todo.id);
    }
}
