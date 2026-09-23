import { Component, markup, useState } from "@odoo/owl";
import { Counter } from "./counter/counter";
import { Card } from "./card/card";
import { TodoList } from "./todo_list/todo_list";

export class Playground extends Component {
    static template = "awesome_owl.playground";
    static components = { Counter , Card, TodoList };
    setup() {
        this.sum = useState({ value: 0 });
    }
    
    escape_value = "<div>some html</div>";
    unescape_value = markup("<div>some html</div>");

    onChange() {
        this.sum.value += 1;
    }
}

// this.onChange = this.onChange.bind(this)