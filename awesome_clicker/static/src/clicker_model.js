import { Reactive } from "@web/core/utils/reactive";


export class ClickerModel extends Reactive {
    constructor() {
        super();
        this.clicks = 10000;
        this.level = 0;
        this.bots = {
            clickbot: {
                price: 1000,
                level: 1,
                increment: 10,
                purchased: 0,
            },
            bigbot: {
                price: 5000,
                level: 2,
                increment: 100,
                purchased: 0,
            }
        };
        this.multiplier = 1;
        this.ticks = 0;
    }

    addClick() {
        this.increment(1);
    }

    increment(num) {
        this.clicks += num;
    }

    tick() {
        this.ticks++;
        for (const bot in this.bots) {
            this.clicks += this.bots[bot].increment * this.bots[bot].purchased * this.multiplier;
        }
    }

    buyMultiplier() {
        if (this.clicks < 50000) {
            return false;
        }
        this.clicks -= 50000;
        this.multiplier++;
    }

    buyBot(name) {
        if (!Object.keys(this.bots).includes(name)) {
            throw new Error(`Invalid bot name ${name}`);
        }
        if (this.clicks < this.bots[name].price) {
            return false;
        }

        this.clicks -= this.bots[name].price;
        this.bots[name].purchased += 1;
    }
}