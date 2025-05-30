import { Component, useState } from "@odoo/owl";
import { TodoItem } from "./todo_item";
import { useAutofocus } from "../utils";

export class TodoList extends Component {
  static template = "awesome_owl.todo_list";
  setup() {
    this.state = useState({ todos: [] });
    this.nextId = 1;
    useAutofocus("inputTodo");
  }

  static components = { TodoItem };

  addTodo(desc) {
    if (desc.keyCode === 13 && desc.target.value != "") {
      this.state.todos.push({
        id: this.nextId++,
        description: desc.target.value,
      });
      desc.target.value = "";
    }
  }
  delete(id) {
    // find the index of the element to delete
    const index = this.state.todos.findIndex((elem) => elem.id === id);
    if (index >= 0) {
      // remove the element at index from list
      this.state.todos.splice(index, 1);
    }
  }
}
