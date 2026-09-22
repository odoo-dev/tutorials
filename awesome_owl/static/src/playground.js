import { Component, markup, useState } from "@odoo/owl";
import { Counter } from "./counter/counter";
import { Card } from "./card/card";

export class Playground extends Component {
    static template = "awesome_owl.playground";
    static components = { Counter , Card};
    setup() {
        this.sum = useState({ value: 0 });
    }
    
    escape_value = "<div>some html</div>";
    unescape_value = markup("<div>some html</div>");

    onChange() {
        this.sum.value += 1;
        console.info("LALALALLALA", this.sum)
    }
}

// this.onChange = this.onChange.bind(this)