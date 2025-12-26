import { Component } from "@odoo/owl";
import { TodoItem } from "../todo_item/todo_item";

export class TodoList extends Component {
  static props = {};
  static template = "todo.playground";
  static components = { TodoItem };

  setup() {
    this.state = useState({
      todos: [],
    });
  }

  findIndex(id) {
    return this.state.todos.findIndex((todo) => todo.id == id);
  }

  onAddTodo(todo) {
    this.state.todos.push(todo);
  }

  onRemoveTodo(id) {
    const index = findIndex(id);
    if (index < 0) return;
    this.state.todos.splice(index);
  }

  onCompleteTodo(id) {
    const index = findIndex(id);
    const el = this.state.todos[index];
    this.state.todos[index] = { ...el, isCompleted: true };
  }
}
