import {Component, markup, useState} from "@odoo/owl";

import {Card} from "./card/card";
import {ExpenseTracker} from "./expense_tracker/expense_tracker";


export class Playground extends Component {
    static template = "expense_tracker.playground";
    static components = {
        Card,
        ExpenseTracker
    };

    setup() {
        this.htmlContent1 = markup("Some <strong>bold</strong> text content.");
        this.htmlContent2 = markup("<span class='text-primary'>Reusable</span> components are great!");

        this.counter = useState({
            value1: 0,
            value2: 0,
        });
    }


}
