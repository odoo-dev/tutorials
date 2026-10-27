import { Component } from "@odoo/owl";
import { Root } from "./product_card/root";

export class Playground extends Component {
    static template = "awesome_owl.playground";
    static components = { Root };
}
