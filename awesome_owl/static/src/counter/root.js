import { Component } from "@odoo/owl";
import { Counter } from "./counter"


export class Root extends Component {
    static components = { Counter }
    static template = "tutorial.root"
}