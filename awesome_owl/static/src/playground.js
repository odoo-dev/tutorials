/** @odoo-module **/

import { Component, useState } from "@odoo/owl";


export class Playground extends Component {
    static template = "awesome_owl.playground";


    state = useState({ value: 0 }); 
    // state = { value: 0 };

    increment() {
        this.state.value++;
    }
}

