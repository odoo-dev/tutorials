/** @odoo-module **/

import { Component, xml, useState, useExternalListener, useRef } from "@odoo/owl";
import TodoItem from  "../todoitem/todoitem"

export default class TodoList extends Component {
    static template = xml`
        <div class="card d-inline-block m-2">
            <div class="card-body">
                <input type="text" placeholder="Add a todo..." t-ref="elementToAdd"/>
                <t t-foreach="todos.value" t-as="i" t-key="i.id">
                    <p><TodoItem todo="i"/></p>
                </t>
            </div>
        </div>`;

    static components = {TodoItem}

    elementToAddRef = useRef("elementToAdd");

    setup() {
        this.todos = useState({value:[]});

        useExternalListener(window, 'keyup', this.addTodo);
    }

    addTodo(ev) {
        if(ev.keyCode === 13) {
            this.todos.value.push({id: this.todos.value.length + 1, description: this.elementToAddRef.el.value, isCompleted: false});
            this.elementToAddRef.el.value = "";
        }
    }
}
