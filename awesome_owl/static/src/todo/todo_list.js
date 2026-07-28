import { Component, useState } from "@odoo/owl";
import { TodoItem } from "./todo_item"

export class TodoList extends Component {
    static template = "awesome_owl.TodoList";
    static components = { TodoItem };

    setup(){
        this.currentId = 3
        this.todos = useState([
            { id: 3, description: "buy milk", isCompleted: false },
            { id: 2, description: "buy egg", isCompleted: true },
            { id: 1, description: "buy water", isCompleted: false }
        ]);
        // this.todos = useState([])
    }

    addTodo(ev) {
        if (ev.keyCode === 13 && ev.target.value != "") {
            this.todos.push({
                id: ++this.currentId,
                description: ev.target.value,
                isCompleted: false
            });
            ev.target.value = "";
        }
    }

    toggleState(todoId) {
        const todo = this.todos.find((todo) => todo.id === todoId);
        if (todo) {
            todo.isCompleted = !todo.isCompleted;
        }
    }
}