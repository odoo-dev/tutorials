/** @odoo-module **/
import { Component, onWillStart, onWillRender, useState, onMounted, onWillPatch, onRendered } from "@odoo/owl";
import { useFocus } from "../focushook/useFocus";

export class Counter extends Component {

    static template = "awesome_owl.counter";
    setup() {
        this.state = useState({ value: 0 });

        // onMounted(() => {
        //     // console.log("Counter Mounted");
        // })

        onRendered(() => {
            console.log("Counter Rendered");
        })

     useFocus("myinput");

        // onWillPatch(() => {
        //     console.log("On Will Patch Counter")
        // })
    }

    increment() {
        this.state.value++;
    }
}