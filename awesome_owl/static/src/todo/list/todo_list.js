import {Component, useState} from "@odoo/owl";
import {TodoItem} from "../item/todo_item";

export class TodoList extends Component {
    static template = "awesome_owl.todo_list";

    static components = {TodoItem};

    static props = {
        items: {
            type: Array,
            optional: true,
        }
    }

    setup() {
        this.props.items = useState([
            { id: 1, description: "buy Beer", isCompleted: true },
            { id: 2, description: "buy Chicken", isCompleted: false },
        ])
    }
}
