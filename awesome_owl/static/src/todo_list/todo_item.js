import { Component, xml } from "@odoo/owl";

export class TodoItem extends Component {
  static template = xml`
    <div t-att-class="{'text-muted': props.todo.isCompleted, 'text-decoration-line-through': props.todo.isCompleted}">
      <input class="m-1" type="checkbox" t-att-checked="props.todo.isCompleted" t-on-change="toggleState"/>
      <span t-esc="props.todo.id+'. '" />
      <t t-esc="props.todo.description" />
      <span style="color: red" class="fa fa-remove m-1" t-on-click="()=>props.removeTodo(props.todo.id)"/>
    </div>`;

    static props = {
    todo: {
      values: {
        id: Number,
        description: String,
        isCompleted: Boolean,
      },
    },
    removeTodo: Function
  };

  toggleState() {
    console.log(this.props.todo.id);
    this.props.todo.isCompleted = !this.props.todo.isCompleted;
  }

}
