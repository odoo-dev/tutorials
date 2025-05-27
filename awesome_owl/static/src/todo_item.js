
import { Component, useState } from "@odoo/owl";

export class TodoItem extends Component {
    static template = "awesome_owl.todo_item";
    
    setup() {
        this.todo = this.props.todo
        this.removeChild = this.props.removeChild
    }

    toggleDone() {
        this.todo.done = !this.todo.done
    }
    
    removeParentsChild() {
        this.removeChild(this.todo.id)
    }
}
