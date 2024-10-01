/** @odoo-module **/

import {registry} from "@web/core/registry";
import {reactive} from "@odoo/owl";


export const clickerService = {
    start(env) {
        const state = reactive({
            counter: 0,
            level: 0,
            clickBots: 0,
        });

        const params = {
            interval: 10000,
            clickPerBot: 10,
        }

        document.addEventListener("click", () => {
            increment(1);
        });

        setInterval(() => {
            increment(state.clickBots * params.clickPerBot);
        }, params.interval);

        function increment(inc) {
            state.counter += inc;
            if (state.level < 1 && state.counter >= 1000) {
                state.level++;
            }
        }

        function buyBot() {
            const clickBotPrice = 1000;
            if (state.counter < clickBotPrice) {
                return false;
            }
            state.counter -= clickBotPrice;
            state.clickBots++;
        }

        return {
            state,
            params,
            increment,
            buyBot,
        };
    },
};

registry.category("services").add("clicker_service", clickerService);
