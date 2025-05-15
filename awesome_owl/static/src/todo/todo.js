/** @odoo-module **/

import { Component, onMounted, useRef, useState } from "@odoo/owl";
import { useAutofocus } from "../utils";

export class TodoItem extends Component {
    static template = "awesome_owl.todo_item";
    static props = {
        todo: {
            type: Object,
            shape: {
                id: Number,
                description: String,
                isCompleted: Boolean,
            }
        },
        toggleState: Function,
        removeTodo: Function,
    };
}

export class TodoList extends Component {
    static template = "awesome_owl.todo_list";
    static components = { TodoItem };

    setup() {
        this.todos = useState([])
        this.idCount = useState({'value': 1});
        useAutofocus("input_todo")
    }

    addTodo(ev) {
        if (ev.keyCode === 13 && ev.target.value) {
            this.todos.push({
                id: this.idCount.value,
                description: ev.target.value,
                isCompleted: false,
            });
            this.idCount.value++;
            ev.target.value = "";
        }
    }

    toggleState(id) {
        const todo = this.todos.find(todo => todo.id === id);
        if (todo) {
            todo.isCompleted = !todo.isCompleted;
        }
    }

    removeTodo(id) {
        const index = this.todos.findIndex((todo) => todo.id === id);
        if (index >= 0) {
              this.todos.splice(index, 1);
        }
    }
}
