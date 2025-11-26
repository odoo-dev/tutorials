import { TodoItem } from "./todo_item";

const { Component, useState, useRef, onMounted } = owl;

export class TodoList extends Component {
  static template = "awesome_owl.todo_list";
  static components = { TodoItem };
  //   todos = useState([
  //     { id: 3, description: "buy milk", isCompleted: false },
  //     { id: 2, description: "find a house", isCompleted: true },
  //     { id: 4, description: "or find a bridge to live under", isCompleted: false },
  //     { id: 7, description: "take out the trash", isCompleted: true },
  //   ]);
  setup() {
    this.todos = useState([]);
    this.myRef = useRef("add_task_input");
    onMounted(() => {
      this.myRef.el.focus();
    });
  }

  curr_id = 0;
  addTodo(ev) {
    if (ev.keyCode === 13 && ev.target.value) {
      let todo = {
        id: ++this.curr_id,
        description: ev.target.value,
        isCompleted: false,
      };
      this.todos.push(todo);
      ev.target.value = "";
    }
  }

  toggleState(id, completed) {
    const todo = this.todos.find((t) => t.id === id);
    if (todo) {
      todo.isCompleted = completed;
    }
  }

  removeTodo(id) {
    const index = this.todos.findIndex((elem) => elem.id === id);
    if (index >= 0) {
      this.todos.splice(index, 1);
    }
  }
}
