/** @odoo-module **/

import { Component, xml } from "@odoo/owl";

export default class TodoItem extends Component {
    static props = {
        todo: {
            id: {type: Number},
            description: {type: String},
            isCompleted: {type: Boolean}
        },
        callbackRemove: {type: Function}
    };

    static template = xml`
        <div>
            <input type="checkbox" t-on-click="toggleCompleted" class="d-inline-block m-2"/>
            <p t-att-class="{'text-muted text-decoration-line-through': props.todo.isCompleted}" class="d-inline-block m-2">
                <t t-out="props.todo.id"/>.    <t t-out="props.todo.description"/>
            </p>
            <span t-on-click="removeTodo" class="fa fa-remove d-inline-block m-2"/>
        </div>`;

    toggleCompleted() {
        this.props.todo.isCompleted = !this.props.todo.isCompleted;
    }

    removeTodo() {
        this.props.callbackRemove(this.props.todo.id);
    }
}
