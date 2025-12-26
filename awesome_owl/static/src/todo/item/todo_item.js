import {Component} from "@odoo/owl";
import {Card} from "../../card/card";

export class TodoItem extends Component {
    static template = "awesome_owl.todo_item";

    static Components = [Card]

    static props = {
        todo: {
            type: Object,
            shape: {
                id: Number,
                description: String,
                isCompleted: Boolean,
            }
        },
        toggleState: {
            type: Function
        },
        removeTodo: {
            type: Function
        }
    }

    changeCheckbox(ev) {
        this.props.toggleState(this.props.todo.id, ev.target.checked);
    }

    removeTodo() {
        this.props.removeTodo(this.props.todo.id)
    }
}
