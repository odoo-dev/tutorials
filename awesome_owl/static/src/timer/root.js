import { Component, signal, computed } from "@odoo/owl";
import { Timer } from "./timer"


export class Root extends Component {
    static components = { Timer }
    static template = "tutorial.timer.root"

}