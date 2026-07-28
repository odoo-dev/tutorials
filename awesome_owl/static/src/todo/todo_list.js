import { Component, useState } from "@odoo/owl";
import { TodoItem } from "./todo_item"

export class TodoList extends Component {
    static template = "awesome_owl.TodoList";
    static components = { TodoItem };

    setup(){
        this.todos = useState([
            { id: 3, description: "buy milk", isCompleted: false },
            { id: 2, description: "buy egg", isCompleted: true },
            { id: 1, description: "buy water", isCompleted: false }
        ]);
    }

}