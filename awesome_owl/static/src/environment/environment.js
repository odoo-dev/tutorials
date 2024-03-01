/** @odoo-module **/

import { Component, useSubEnv, useEnv } from "@odoo/owl";
import { useCustomEnv } from "./customenv";
export class Environment extends Component {
    static template = "awesome_owl.environment";

    setup() {
        this.data = useEnv();
        // useCustomEnv()
        console.log(this.data);
    }
}
