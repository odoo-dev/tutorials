/** @odoo-module **/

import { Component, useState, useRef, onMounted } from "@odoo/owl";
import { ToDoItem } from './todoitem';

export class ToDoList extends Component {
    static template = "awesome_owl.todolist";

    setup() {
        this.todos = useState([]);
        this.state = useState({text: ""});
        this.input_ref = useRef('todo-input');
        onMounted(() => {
            this.input_ref.el.focus();
        });
    }

    addTodo(ev) {
        if (this.state.text == "")
            return;
        if (ev.keyCode === 13) {
            if (this.todos.length == 0)
                var new_id = 0;
            else
                var new_id = this.todos[this.todos.length - 1].id + 1;
            this.todos.push({ id: new_id, description: this.state.text, isCompleted: false});
            this.state.text = "";
        }
    }

    todoChange(val, id) {
        var todo = this.todos.find(item => item.id === id);
        if (todo !== undefined)
            todo.isCompleted = !val;
    }

    removeTodo(id) {
        var toDeleteIndex = this.todos.findIndex(item => item.id === id);
        if (toDeleteIndex >= 0) {
            this.todos.splice(toDeleteIndex, 1);
        }
    }

    static components = { ToDoItem }
}