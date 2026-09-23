import {Component, useState} from "@odoo/owl"
import { TodoItem } from "../todo_item/todo_item";

export class TodoList extends Component {
    static template = 'awesome_owl.todo_list';
    static components = { TodoItem }

    setup(){
        this.todos = useState([
            { id: 3, description: "buy milk", isCompleted: false },
            { id: 4, description: "buy Silk", isCompleted: false },
            { id: 5, description: "Sell PS5", isCompleted: false },
            { id: 6, description: "Update computer", isCompleted: true },
        ]);
    }

}
