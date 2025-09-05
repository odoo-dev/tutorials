/** @odoo-module **/

import { Component, markup } from "@odoo/owl";
import { Counter } from "./counter/counter";
import { Card } from "./card/card";

export class Playground extends Component {
    static template = "awesome_owl.playground"; 
    static components = { Counter, Card };

    html1 = "<div class='text-primary'>some contents</div>";
    html2 = markup("<div class='text-primary'>some contents</div>");
}
