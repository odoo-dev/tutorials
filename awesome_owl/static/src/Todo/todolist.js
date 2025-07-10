/** @odoo-module **/

import { Component, useState, useRef, onMounted } from "@odoo/owl";
import { TodoItem } from "./todoitem";
// import { useAutofocus } from "../../../utils";

export class TodoList extends Component {
    static template = "awesome_owl.todolist";
    static components = {
        TodoItem
    }

    setup() {
        this.nextId = 1;
        this.todos = useState([]);
        this.myRef = useRef('input_box');

        onMounted(() => {
            // console.log(this.myRef.el);
            this.myRef.el.focus();
        })

        // For some reason doesn't work (got 404 error)
        // useAutofocus('input_box');
    }

    addTodo(e) {
        if (e.keyCode == 13 && e.target.value != "") {
            this.todos.push({
                id: this.nextId++,
                description: e.target.value,
                isCompleted: false
            })

            e.target.value = "";
        }
    }

    removeTodo(id) {
        const index = this.todos.findIndex(t => t.id == id);
        if (index >= 0) {
            this.todos.splice(index, 1);
        }
    }

    toggleTodo(id) {
        const todo = this.todos.find(t => t.id == id);
        todo.isCompleted = !todo.isCompleted;
    }

    // increment() {
    //     this.state.value += 1;
    //     if (this.props.onChange) {
    //         this.props.onChange();
    //     }
    // }

}
