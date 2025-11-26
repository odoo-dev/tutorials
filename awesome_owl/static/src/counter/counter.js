const { Component, useState } = owl;

export class Counter extends Component {
  static template = "awesome_owl.counter";
  state = useState({ value: 1 });
  static props = {
    onChange: { type: Function, optional: true },
  };

  increment() {
    this.state.value++;
    if (this.props.onChange != undefined) {
      this.props.onChange();
    }
  }
}
