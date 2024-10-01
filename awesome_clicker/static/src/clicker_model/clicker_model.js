/** @odoo-module **/

import {Reactive} from "@web/core/utils/reactive";

export class ClickerModel extends Reactive {
    constructor() {
        super();
        this.counter = 0;
        this.level = 0;
        this.clickBots = 0;

        // Params
        this.interval = 10000;
        this.clickPerBot = 10;

        document.addEventListener("click", () => {
            this.increment(1);
        });

        setInterval(() => {
            this.increment(this.clickBots * this.clickPerBot);
        }, this.interval);
    }

    increment(inc) {
        this.counter += inc;
        if (this.level < 1 && this.counter >= 1000) {
            this.level++;
        }
    }

    buyBot() {
        const clickBotPrice = 1000;
        if (this.counter < clickBotPrice) {
            return false;
        }
        this.counter -= clickBotPrice;
        this.clickBots++;
    }
}