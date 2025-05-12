import { Component } from "@odoo/owl";

export class TodoItem extends Component {
    static template = "awesome_owl.todoitem";
    static props = {
        item: {
            type: Object,
            shape: {
                id: Number,
                description: String,
                isCompleted: Boolean,
            }
        },
        onToggle: Function,
        onRemoveItem: Function,
    }

    onToggle(e) {
        this.props.onToggle(this.props.item.id, !this.props.item.isCompleted);
    }

    onRemoveItem(e) {
        console.log("Removing line")
        this.props.onRemoveItem(this.props.item.id)
    }
}