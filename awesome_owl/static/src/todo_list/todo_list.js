import { Component, onMounted, useRef, useState } from "@odoo/owl";
import { TodoItem } from "./todo_item";

export class TodoList extends Component {
    static template = "awesome_owl.todo_list";
    static components = { TodoItem };

    setup() {
        this.todos = useState([
            { id: 1, description: "write tutorial", isCompleted: true },
            { id: 2, description: "buy milk", isCompleted: false },
        ]);
        this.todo_counter = 3;
        this.inputRef = useRef("input_field");
        onMounted(() => {
            this.inputRef.el.focus();
        });
    }

    addTodo(ev) {
        if (ev.keyCode == 13 && ev.target.value) {
            this.todos.push({ id: this.todo_counter++, description: ev.target.value, isCompleted: false });
            ev.target.value = "";
        }
    }

    toggleState(todoId) {
        const todo = this.todos.find((t) => t.id === todoId);
        todo.isCompleted = !todo.isCompleted;
    }
}
