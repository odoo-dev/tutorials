import { Component, useState } from "@odoo/owl";

export class Counter extends Component {
    static template = "awesome_owl.counter";

    static props = {
        onChange: {type: Function, optional: true}
    }

    setup(){
        this.number = useState({value : 1});
    }

    increment(){
        this.number.value++;
        console.log(this.props.onChange)
        if (this.props.onChange){
            this.props.onChange()
        }
        
    }
}
