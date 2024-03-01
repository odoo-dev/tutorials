/** @odoo-module **/

import { Component, useState, useEnv, onMounted } from "@odoo/owl";
import { Navbar } from "./navbar/navbar";
import { Counter } from "./counter/counter";
import { Lifecycle } from "./lifecycle/lifecycle";
import { UseEffectExample } from "./useeffect/useEffectExample";
import { UnmountingExample } from "./unmounting/unmounting";
import { Environment } from "./environment/environment";
export class Playground extends Component {
    static components = { Environment, Counter, Navbar, Lifecycle, UseEffectExample, UnmountingExample };
    static template = "awesome_owl.playground";
    setup() {
        this.state = useState({ value: 0 });
    }
    change() {
        this.state.value++;
    }
}
