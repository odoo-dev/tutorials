import { Component, useState } from "@odoo/owl";
import { TodoItem } from "../todo_item/todo_item";

export class TodoList extends Component {
  static props = {};
  static template = "todo.list.playground";
  static components = { TodoItem };

  setup() {
    this.state = useState({
      todos: [],
    });
  }

  findIndex(id) {
    return this.state.todos.findIndex((todo) => todo.id == id);
  }

  onAddTodo() {
    debugger;
    const form = document.getElementById("todo-form");
    const formData = new FormData(form);
    const todo = {
      id: (this.state.todos.at(-1)?.id ?? 0) + 1,
      isCompleted: false,
      description: formData.get("description"),
    };
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
