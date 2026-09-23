import { Component, useRef, useState, xml,onMounted } from "@odoo/owl";
import { TodoItem } from "./todo_item";

export class TodoList extends Component {
    static template = "awesome_owl.todo.list";
    static components = { TodoItem };

    setup() {
        this.todoCurrentId = 1;
        this.todos = useState({value : []});

        this.inputRef = useRef("inputRef")
        onMounted(() => {
            this.inputRef.el.focus();
            console.log(this.inputRef)
        });

    }

    addTodo(ev) {
        if (ev.keyCode === 13) {
            let desc = this.inputRef.el.value;
            if (!desc) {
                return
            }
            this.todos.value.push({id : this.todoCurrentId, description : desc, isCompleted : false});
            this.todoCurrentId++;
            this.inputRef.el.value = "";
        }
    }
}