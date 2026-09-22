import { Component, markup } from "@odoo/owl";
import { Counter } from "./counter/counter";
import { Card } from "./card/card";

export class Playground extends Component {
    static template = "awesome_owl.playground";
    static components = { Counter , Card};
    setup() {
    }
    
    escape_value = "<div>some html</div>";
    unescape_value = markup("<div>some html</div>");
}

