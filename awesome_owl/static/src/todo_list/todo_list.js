import { Component, useState, useRef, onMounted} from "@odoo/owl";
import { TodoItem } from "./todo_item";

export class TodoList extends Component {
  static template = "awesome_owl.todo_list";

  static components = { TodoItem };

  setup() {
    this.state = useState({ todos: [{id:121, description: "do that!", isCompleted: true}], input: "", curr_id: 1 });
    
    this.inputRef = useRef("input");
    onMounted(()=>{
      this.inputRef.el.focus();
    });
  }

  updateTodo(event) {
    if (event.keyCode === 13) {
      this.state.input != "" ? this.addTodo() : "";
      this.state.input = "";
      return;
    }

    this.state.input = event.target.value;
  }

  addTodo() {
    this.state.todos.push({
      id: this.state.curr_id,
      description: this.state.input,
      isCompleted: false,
    });
    this.state.input = "";
    this.state.curr_id++;
  }

  removeTodo(id){
    const index = this.state.todos.findIndex((todo) => todo.id === id);
    if (index >= 0){
      this.state.todos.splice(index, 1);
    }
  }
}
