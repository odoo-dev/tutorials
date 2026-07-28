import { Component, useState } from "@odoo/owl";

export class TodoItem extends Component {
    static template = "awesome_owl.TodoItem";
    static props = {
        todo: {
            id: Number,
            decription: String,
            isCompleted: Boolean,
        },
        toggleCheck: Function
    }

    onCheck () {
        this.props.toggleCheck(this.props.todo.id);
    }

}