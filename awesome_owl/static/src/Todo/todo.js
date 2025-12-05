import { Component, useState, useRef, onMounted } from '@odoo/owl'

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
            // { id: 1, description: "create todolist component", isCompleted: true},
            // { id: 2, description: "create todoitem component", isCompleted: false},
            // { id: 3, description: "display the components", isCompleted: false}
        ]);
        this.inputRef = useRef('todo_desc')
        onMounted(() => {
            console.log(this.inputRef.el);
            this.inputRef.el.focus();
        })
    }

    addTodo(event, description){
        description = description.trim()
        if (event.key === "Enter" && description){
            console.log("this: ",this)
            console.log("this.todos: ", this.todos)
            this.todos.push({
                id: this.todos.length + 1,
                description: description,
                isCompleted: false
            });
            event.target.value = ""
        }
    }
}