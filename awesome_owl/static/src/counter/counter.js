import { Component, useState, xml } from "@odoo/owl";

export class Counter extends Component {
    static template = xml` <button t-on-click="increment"> Click Me! [<t t-esc="state.value"/>] </button>`;
    static props = {
        callback : {type : Function, optional: true},
    }
    setup() {
        this.state = useState({ value: 0 });
        console.info(this.props)
    }
    
    increment() {
        this.state.value++;
        //todo
        this.props.callback()
    }

}