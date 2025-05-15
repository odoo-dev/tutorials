/** @odoo-module **/

import { useState, xml, Component, markup } from "@odoo/owl";
import { Card } from "./card/card";
import { Counter } from "./counter/counter";
import { TodoList } from "./todo/todo";

export class Playground extends Component {
    static template = "awesome_owl.playground";
    static components = { Card, Counter, TodoList };

    setup() {
        this.content1 = "<div class='text-primary'>some content</div>";
        this.content2 = markup("<div class='text-primary'>some content</div>");
        this.sum = useState({ value: 0 });
    }

    incrementSum() {
        this.sum.value++;
    }
}
