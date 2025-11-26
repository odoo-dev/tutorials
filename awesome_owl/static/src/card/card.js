const { Component, useState } = owl;

export class Card extends Component {
  static template = "awesome_owl.card";
  static props = {
    title: String,
    slots: {type: Object, optional: true}
  };
  state = useState({ isCollapsed: true })

  collpaseCard(){
    this.state.isCollapsed = !this.state.isCollapsed;
  }
}
