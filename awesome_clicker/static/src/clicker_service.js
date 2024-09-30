/** @odoo-module **/

import {registry} from "@web/core/registry";
import {reactive} from "@odoo/owl";


export const clickerService = {
    start(env) {
        const state = reactive({counter: 0});

        document.addEventListener("click", () => {
            state.counter++;
        });

        function increment(inc) {
            state.counter += inc;
        }

        return {
            state,
            increment,
        };
    },
};

registry.category("services").add("clicker_service", clickerService);
