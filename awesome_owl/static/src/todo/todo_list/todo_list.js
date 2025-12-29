import { Component, onMounted, useState, useRef } from "@odoo/owl";
import { TodoItem } from "../todo_item/todo_item";

export class TodoList extends Component {
  static props = {};
  static template = "todo.list.playground";
  static components = { TodoItem };

  setup() {
    this.state = useState({
      todos: [],
    });
    this.descriptionRef = useRef("description_ref");

    onMounted(() => {
      this.descriptionRef?.el?.focus();
    });

    this.findIndex = this.findIndex.bind(this);
    this.onRemoveTodo = this.onRemoveTodo.bind(this);
    this.onCompleteTodo = this.onCompleteTodo.bind(this);
  }

  findIndex(id) {
    return this.state.todos.findIndex((todo) => todo.id == id);
  }

  onAddTodo() {
    const form = document.getElementById("todo-form");
    const formData = new FormData(form);
    const description = formData.get("description");
    if (!description) return;

    const todo = {
      id: (this.state.todos.at(-1)?.id ?? 0) + 1,
      isCompleted: false,
      description,
    };
    this.state.todos.push(todo);
    form.reset();
  }

  onRemoveTodo(id) {
    const index = this.findIndex(id);
    if (index < 0) return;
    this.state.todos.splice(index, 1);
  }

  onCompleteTodo(id) {
    debugger;
    const index = this.findIndex(id);
    const el = this.state.todos[index];
    this.state.todos[index] = { ...el, isCompleted: true };
  }
}
