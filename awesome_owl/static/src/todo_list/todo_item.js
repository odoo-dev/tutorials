const { Component } = owl;

export class TodoItem extends Component {
  static template = "awesome_owl.todo_item";
  static props = {
    todo: {
      type: Object,
      shape: { id: Number, description: String, isCompleted: Boolean },
    },
    toggleState: Function,
    removeTodo: Function,
  };

  toggleState(ev) {
    const id = this.props.todo.id;
    const checked = ev.target.checked;
    if (checked != this.props.todo.isCompleted) {
      this.props.toggleState(id, checked);
    }
  }

  removeTodo(env){
    const id = this.props.todo.id;
    this.props.removeTodo(id);
  }
}
