import { Component, useState } from '@odoo/owl'

export class TodoItem extends Component {
    static template = "awesome_owl.todoitem"
    static props = {
        todo: {
            id: { type: Number },
            description: { type: String },
            isCompleted: { type: Boolean }
        }
    }
}

export class TodoList extends Component {
    static template = "awesome_owl.todolist";
    static components = { TodoItem }

    setup(){
        this.todos = useState([
            { id: 1, description: "create todolist component", isCompleted: true},
            { id: 2, description: "create todoitem component", isCompleted: false},
            { id: 3, description: "display the components", isCompleted: false}
        ])
    }
}