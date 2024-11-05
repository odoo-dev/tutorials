import { Reactive } from "@web/core/utils/reactive";
import { EventBus } from "@odoo/owl";
import { rewards } from "./click_rewards";
import { choose } from "./utils";
import { CURRENT_VERSION } from "./clicker_migration";


export class ClickerModel extends Reactive {
    constructor() {
        super();
        this.version = CURRENT_VERSION;
        this.bus = new EventBus();
        this.clicks = 0;
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
            },
            superbot: {
                price: 10000,
                level: 3,
                increment: 1000,
                purchased: 0,
            }
        };
        this.trees = {
            pear: {
                price: 1000000,
                level: 5,
                product: "pear",
                purchased: 0,
            },
            cherry: {
                price: 10000000,
                level: 5,
                product: "cherry",
                purchased: 0,
            }
        };
        this.fruits = {
            pear: 0,
            cherry: 0,
        }
        this.multiplier = 1;
        this.ticks = 0;
    }

    addClick() {
        this.increment(1);
    }

    increment(num) {
        this.clicks += num;

        if(this.unlocks[this.level] && this.unlocks[this.level].clicks <= this.clicks) {
            this.bus.trigger("UNLOCK", this.unlocks[this.level]);
            this.level++;
        }
    }

    tick() {
        this.ticks++;
        for (const bot in this.bots) {
            this.clicks += this.bots[bot].increment * this.bots[bot].purchased * this.multiplier;
        }
        if(this.ticks % 3 == 0) {
            for (const tree in this.trees) {
                this.fruits[this.trees[tree].product] += this.trees[tree].purchased;
            }
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

    buyTree(name) {
        if (!Object.keys(this.trees).includes(name)) {
            throw new Error(`Invalid tree name ${name}`);
        }
        if (this.clicks < this.trees[name].price) {
            return false;
        }

        this.clicks -= this.trees[name].price;
        this.trees[name].purchased += 1;
    }

    giveReward() {
        const availableReward = [];
        for (const reward of rewards) {
            if (reward.minLevel <= this.level || !reward.minLevel) {
                if (reward.maxLevel >= this.level || !reward.maxLevel) {
                    availableReward.push(reward);
                }
            }
        }
        const reward = choose(availableReward);
        this.bus.trigger("REWARD", reward);
        return choose(availableReward);
    }

    get unlocks() {
        return [
            { clicks: 1000, unlock: "clickbot" },
            { clicks: 5000, unlock: "bigbot" },
            { clicks: 10000, unlock: "superbot" },
            { clicks: 100000, unlock: "multiplier" },
            { clicks: 1000000, unlock: "pear and cherry trees" },
        ];
    }

    toJSON() {
        const json = Object.assign({}, this);
        delete json["bus"];
        return json;

    }

    static fromJSON(json) {
        const clicker = new ClickerModel();
        const clickerInstance = Object.assign(clicker, json);
        return clickerInstance;
    }
}