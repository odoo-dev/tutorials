
import { Component, useState, useRef, onMounted } from "@odoo/owl";
import { TodoItem } from "./todo_item"

export class TodoList extends Component {
    static template = "awesome_owl.todo_list";
    static components = { TodoItem }
    
    setup() {
        this.todos = useState([{ id: 1, content: "A", done: false }, { id: 2, content: "B", done: false }, { id: 3, content: "C", done: true }, { id: 4, content: "D", done: false }]);
        this.todo_input = useRef('todo_input');
        onMounted(() => {
            this.todo_input.el.focus();
            this.nextTodoId = this.findMaxId(this.todos);
        });
        this.removeChild=this.removeChild.bind(this);
    }
    
    findMaxId(list) {
        var currentmax = 0;
        for (var i in list) {
            if (list[i].id > currentmax) currentmax = list[i].id;
            console.log(currentmax)
            console.log(i)
            console.log(list[i])
        }
        return currentmax+1;
    }
    
    addTodo(ev) {
        if ((this.todo_input.el.value != "") && (ev.keyCode === 13)) {
            let newTodo = { id: this.nextTodoId, content: this.todo_input.el.value, done: false};
            this.todos.push(newTodo);
            this.todo_input.el.value = "";
            this.nextTodoId = this.findMaxId(this.todos);
        }
    }
    
    removeChild(childId) {
        const index = this.todos.findIndex((elem) => elem.id === childId);
        if (index >= 0) {
            this.todos.splice(index, 1);
        }
        this.nextTodoId = this.findMaxId(this.todos);
    }

}
