/** @odoo-module **/

import { Component, useState } from "@odoo/owl";

export class ToDoItem extends Component {
    static template = "awesome_owl.todoitem";

    setup() {
        this.state = useState({checkboxState : false});
    }

    onCheckboxStateChange() {
        this.props.onChange(this.state.checkboxState, this.props.id)
    }

    onDeleteClick() {
        this.props.removeTodo(this.props.id);
    }

    static props = {
        id : {type: Number}, 
        description : {type: String},
        isCompleted : {type: Boolean},
        onChange : {type: Function},
        removeTodo : {type: Function}
    }
}