/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { Counter } from "./counter/counter";
import { Card } from "./card/card";

export class Playground extends Component {
    static template = "awesome_owl.playground";

    static components = { Counter, Card };

    setup() {
        this.total_sum = useState({ value: 0 });
    }

    incrementSum() {
        this.total_sum.value++;
    }
}
