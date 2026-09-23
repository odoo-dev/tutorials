import { Component, useState, xml } from "@odoo/owl";
import { TodoItem } from "./todo_item";

export class TodoList extends Component {
    static template = "awesome_owl.todo.list";
    static components = { TodoItem };

    setup() {
        this.todoCurrentId = 1;
        this.todos = useState({value : []});
    }

    addTodo(ev) {
        if (ev.keyCode === 13) {
            const inputField = document.getElementById("new_todo");
            let desc = inputField.value;
            if (!desc) {
                return
            }
            this.todos.value.push({id : this.todoCurrentId, description : desc, isCompleted : false});
            this.todoCurrentId++;
            inputField.value = "";
        }
    }
}