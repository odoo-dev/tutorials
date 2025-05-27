/** @odoo-module **/

import { Component, markup } from "@odoo/owl";
import { Counter } from "./counter";
import { Card } from "./card";
import { TodoList } from "./todo_list"

export class Playground extends Component {
    static template = "awesome_owl.playground";
    static components = { Card, TodoList, Counter };

    setup() {
        console.log("play")
        this.markedb = markup("<b>B</b>");
        this.unmarkedb = "<b>B</b>";
    }
}
