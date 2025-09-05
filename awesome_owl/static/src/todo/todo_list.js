/** @odoo-module **/

import { Component, useState, onMounted, useRef } from "@odoo/owl";
import { TodoItem } from "./todo_item";

export class TodoList extends Component {
    static template = "awesome_owl.TodoList";
    static components = { TodoItem };

    setup(){
        this.todos = useState([]);
        this.inputRef = useRef("newTodoInput");
        onMounted(() => {
            this.inputRef.el.focus();
        });
    }

    addTodo(ev) {
        if (ev.keyCode === 13 && ev.target.value.trim().length > 0) {
            this.todos.push({
                id: this.todos.length + 1,
                description: ev.target.value,
                isCompleted: false,
            });
            ev.target.value = "";
        }
    }
}