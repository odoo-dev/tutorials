import {Counter} from "./counter/counter"
import {Card} from "./card/card"
import {Component, markup, useState} from "@odoo/owl";


export class Playground extends Component {
    static template = "awesome_owl.playground";

    static components = {Counter, Card};
    title = "<i>Card 1</i>"
    card_content = markup('<a href="http://">link</a>')

    incrementSum() {
        console.log('incrementSum');
        this.state.total++;
    }

    setup() {
        console.log('setup');
        this.state = useState({
            'total': 0
        });
    }
}
