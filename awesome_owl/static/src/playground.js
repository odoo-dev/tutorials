import { Component, useState } from "@odoo/owl";
import { Counter } from "./counter/counter";
import { Card } from "./card/card";
import { TodoList } from "./todo/todo_list/todo_list";

const COUNTERS_INIT = [
  {
    id: 1,
    value: 0,
  },
  {
    id: 2,
    value: 0,
  },
];

export class Playground extends Component {
  static props = {};
  static template = "owl.playground";
  static components = { Counter, Card, TodoList };

  setup() {
    this.state = useState({ sum: 0, counters: COUNTERS_INIT });
    this.onIncrement = this.onIncrement.bind(this);
  }

  syncSum() {
    this.state.sum++;
  }

  onIncrement(id) {
    debugger;
    const updatedCounters = this.state.counters.map((counter) => {
      if (counter.id === id)
        return {
          ...counter,
          value: counter.value + 1,
        };

      return counter;
    });

    this.state.counters = updatedCounters;
    this.syncSum();
  }
}
