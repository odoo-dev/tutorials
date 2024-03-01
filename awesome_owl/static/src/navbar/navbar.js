/** @odoo-module **/
import { Component, useState } from "@odoo/owl";

export class Navbar extends Component {
    static template = "owl_playground.navbar";
    setup() {
        this.state = useState({ value: "Welcome To OWL Session 🦉" });
    };

    increment() {
        this.state.value = this.state.value === "Welcome To OWL Session 🦉" ? "OWL is Not for Beginners 🐶" : "Welcome To OWL Session 🦉";
    }
}