/** @odoo-module **/

import {Component, onMounted, useRef, useState} from "@odoo/owl";
import {TodoItem} from "./todoitem";

export class TodoList extends Component {
    static template = "awesome_owl.TodoList";
    static components = {TodoItem};

    setup() {
        this.state = useState({
            todos: [{id: 1, description: "buy milk 1", isCompleted: false}, {
                id: 2,
                description: "buy milk 2",
                isCompleted: false
            }, {
                id: 3, description: "buy milk 3", isCompleted: true
            }], nextId: 4, newTodoText: ""
        });

        this.inputTodoRef = useRef('inputTodo');

        onMounted(() => {
            this.inputTodoRef.el.focus();
        });
    }

    addTodo(ev) {
        if (ev.keyCode === 13 && this.state.newTodoText.trim()) {
            this.state.todos.push({
                id: this.state.nextId, description: this.state.newTodoText, isCompleted: false
            });
            this.state.nextId++;
            this.state.newTodoText = "";
        }
    }

    toggleTodoState(todoId) {
        const todo = this.state.todos.find(t => t.id === todoId);
        if (todo) {
            todo.isCompleted = !todo.isCompleted;
        }
    }

    removeTodo(todoId) {
        const index = this.state.todos.findIndex(t => t.id === todoId);
        if (index >= 0) {
            this.state.todos.splice(index, 1);
        }
    }
}