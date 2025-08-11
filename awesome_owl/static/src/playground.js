/** @odoo-module **/

import {Component, useState} from "@odoo/owl";
import {Counter} from "./counter/counter";
import {Card} from "./card/card";
import {TodoList} from "./todo/todolist";

export class Playground extends Component {
    static template = "awesome_owl.Playground";
    static components = {Counter, Card, TodoList};

    setup() {
        this.state = useState({counterSum: 2});
    }

    onIncrement() {
        this.state.counterSum++;
    }
}
