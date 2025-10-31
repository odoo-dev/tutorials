/** @odoo-module **/

import { Component, markup, useState } from "@odoo/owl";
import { Counter } from "./counter/counter";
import { Card } from "./card/card";
import { TodoList } from "./todo/todolist";

export class Playground extends Component {
    static template = "awesome_owl.playground";

    static components = {Counter, Card, TodoList}

    setup(){
            this.content = "<a href=''> hyperlien </a>";
            this.contentMarkup = markup("<a href=''> hyperlien </a>");
            this.sum = useState({value : 2});
            this.incrementSum = this.incrementSum.bind(this);
        }

    incrementSum(){
        this.sum.value++;
    }
}
