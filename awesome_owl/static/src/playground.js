import {Component, markup} from "@odoo/owl";
import { Card } from "./card/card"
import { Counter } from "./counter/counter"

export class Playground extends Component {
    static template = "awesome_owl.playground";
    static components = { Card , Counter };

    card1Text = '<div class=\'text-primary\'>some content</div>'
    card2Text = markup(this.card1Text)
}
