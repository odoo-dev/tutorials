const { Component, markup, useState } = owl;
import { Card } from "./card/card";
import { Counter } from "./counter/counter";
import { TodoList } from "./todo_list/todo_list";

export class Playground extends Component {
  static template = "awesome_owl.playground";
  static components = { Counter, Card, TodoList };
  title = "Hello this is me";

  state = useState({ sum: 2 });

  onChange() {
    this.state.sum++;
  }
}
