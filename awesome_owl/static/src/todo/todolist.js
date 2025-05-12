import { Component, useState } from "@odoo/owl";
import { TodoItem } from "./todoitem";

export class TodoList extends Component {
    static template = "awesome_owl.todolist";
    static components = { TodoItem };

    setup() {
        this.todoitems = useState([]);
        this.todoitems_curr_id = useState({ value: 0 });
    }

    onTextInputKeyup(e) {
        if (e.keyCode === 13) { // Enter
            input_box = document.getElementById("input_box");
            if (input_box.value.length === 0) return;

            this.todoitems.push({
                id: this.todoitems_curr_id.value,
                description: input_box.value,
                isCompleted: false,
            })
            this.todoitems_curr_id.value++;
            input_box.value = ""
        }
    }

    updateToggleState(id, state) {
        const updated_item = this.todoitems.find(obj => obj.id === id);
        updated_item.isCompleted = state;
    }

    removeItem(id) {
        const index = this.todoitems.findIndex((item) => item.id === id);
        if (index >= 0) {
            this.todoitems.splice(index, 1);
        }
    }
}