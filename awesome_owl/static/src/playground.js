/** @odoo-module **/
import { Component, useState, markup } from "@odoo/owl"
import { Counter } from "./counter/counter";
import { Card } from "./card/card";
import { TodoList } from "./todo/todolist";
import { TodoItem } from "./todo/todoitem";

export class Playground extends Component {
    static template = "awesome_owl.playground";
    static components = { Counter, Card, TodoList, TodoItem };

    setup() {
        this.card_content = markup("<div class='class-primary'>some content</div>");
        this.sum = useState({ value: 0 });
    }

    onCounterChange() {
        this.sum.value++;
    }
}
