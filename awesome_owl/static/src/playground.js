/** @odoo-module **/

import { Component, markup, useState } from "@odoo/owl";
import { Counter } from "./counter/counter";
import { Card } from "./card/card";
import { ToDoList } from "./todolist/todolist";

export class Playground extends Component {
    static template = "awesome_owl.playground";

    incrementSum() {
        this.sum.value += 1;
    }

    setup() {
        this.sum = useState({ value: 0});
        this.card1 = {
            title: "card 1",
            content: markup("content of card 1")
        };
        this.card2 = {
            title: "card 2",
            content: markup("<i>content of card 2</i>")
        };
    }

    static components = { Counter, Card, ToDoList };
}
