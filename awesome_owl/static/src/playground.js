/** @odoo-module **/

import { markup, Component, useState } from "@odoo/owl";
import { Counter } from "./Counter/counter";
import { Card } from "./Card/card";
import { TodoList } from "./Todo/todolist";

export class Playground extends Component {
    static template = "awesome_owl.playground";
    static components = {
        Counter,
        Card,
        TodoList,
    };

    // setup() {
        // this.state = useState({ sum: 2 });
        // this.content1="<div class='text-primary'>some content</div>";
        // this.content2=markup`<div class='text-primary'>some content</div>`;
    // }

    // incrementSum() {
    //     this.state.sum += 1;
    // }


}
