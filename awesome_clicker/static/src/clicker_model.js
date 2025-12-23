import { Reactive } from "@web/core/utils/reactive";
import { EventBus } from "@odoo/owl";
import { rewards } from "./click_rewards";
import { choose } from "./utils";

export class ClickerModel extends Reactive {
    constructor() {
        super();
        this.clicks = 0;
        this.level = 0;
        this.bus = new EventBus();
        this.power = 1;
        this.bots = {
            clickbots: {
                price: 1000,
                level: 1,
                increment: 10,
                purchased: 0,
            },
            bigbots: {
                price: 5000,
                level: 2,
                increment: 100,
                purchased: 0,
            },
        };
        this.clicksPerSecond = 0;

        document.addEventListener("click", () => this.increment(1), true);
        setInterval(() => {
            for (const bot in this.bots){
                this.increment(this.bots[bot].increment * this.bots[bot].purchased * this.power);
            }
        }, 1000);
    }

    increment(inc) {
        this.clicks += inc;
        if(
            this.milestones[this.level] &&
            this.clicks >= this.milestones[this.level].clicks
        ) {
            this.bus.trigger("MILESTONE", this.milestones[this.level]);
            this.level += 1;
            console.log("new level: " + this.level)
        }
    }

    buyBot(name) {
        if (!Object.keys(this.bots).includes(name)){
            throw new Error('Invalid bot name ${name}');
        }
        if (this.clicks < this.bots[name].price){
            return false;
        }

        this.clicks -= this.bots[name].price;
        this.bots[name].purchased++;
        this.updateClicksPerSecond();
    }

    updateClicksPerSecond(){
        const totalCPS = Object.values(this.bots).reduce((total, bot) => {
            return total + (bot.increment * bot.purchased * this.power);
        }, 0);
        this.clicksPerSecond = totalCPS;
    }

    buyPower(){
        const powerPrice = 50000;
        if (this.clicks < powerPrice) {
            return false;
        }
        this.clicks -= powerPrice;
        this.power += 1;
    }

    get milestones() {
        return [
            { clicks: 1000, unlock: "clickBot" },
            { clicks: 5000, unlock: "bigBot" },
            { clicks: 100000, unlock: "power" },
        ];
    }

    getReward(){
        const availableRewards = rewards.filter(reward => {
            const minLevel = reward.minLevel ?? 0;
            const maxLevel = reward.maxLevel ?? Infinity;

            return this.level >= minLevel && this.level <= maxLevel;
        });
        const reward = choose(availableRewards);
        this.bus.trigger("REWARD", reward);
        return reward;
    }
}
