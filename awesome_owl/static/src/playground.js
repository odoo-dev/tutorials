/** @odoo-module **/

import { Component, markup, useState } from "@odoo/owl";
import { Counter } from "./counter/counter";
import { Card } from "./card/card";
import { TodoList } from "./todo/todo_list";

export class Playground extends Component {
    static template = "awesome_owl.playground"; 
    static components = { Counter, Card, TodoList };

    setup() {
        this.sum = useState({ value: 0 });
        this.html1 = "<div class='text-primary'>some contents</div>";
        this.html2 = markup("<div class='text-primary'>some contents</div>");
    }

    incrementSum() {
        this.sum.value++;
    }
}
