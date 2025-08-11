/** @odoo-module **/

import {Component} from "@odoo/owl";

export class TodoItem extends Component {
    static template = "awesome_owl.TodoItem";

    static props = {
        todo: {
            type: Object, shape: {
                id: {type: Number, optional: false},
                description: {type: String, optional: false},
                isCompleted: {type: Boolean, optional: true, default: false},
            }, required: true,
        },
        toggleState: {type: Function, required: true},
        removeTodo: {type: Function, required: true}
    };

    onCheckboxChange() {
        this.props.toggleState(this.props.todo.id);
    }

    onRemoveClick() {
        this.props.removeTodo(this.props.todo.id);
    }
}