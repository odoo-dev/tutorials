import { Reactive } from "@web/core/utils/reactive";
import { EventBus } from "@odoo/owl";
import { rewards } from "../click_rewards";
import { choose } from "../utils/utils";
import { browser } from "@web/core/browser/browser";
import { CURRENT_VERSION } from "../clicker_migration";
import { migrate } from "../clicker_migration";

export class ClickerModel extends Reactive {
  constructor() {
    super();

    const oldClicker = JSON.parse(browser.localStorage.getItem("clicker"));
    console.log(oldClicker);

    if (oldClicker) {
      Object.assign(this, oldClicker);
    } else {
      this.clicks = 999990;
      this.level = 0;
      this.bots = {
        clickBots: 0,
        bigBots: 0,
      };
      this.power = 1;
      this.trees = [
        {
          name: "pear",
          trees_nb: 0,
          fruits_nb: 0,
        },
        {
          name: "cherry",
          trees_nb: 0,
          fruits_nb: 0,
        },
        { name: "peach", trees_nb: 0, fruits_nb: 0, price: 1500000 },
      ];
    }

    this.bus = new EventBus();
    this.version = CURRENT_VERSION;
    if (this.clicks >= 1000000 && this.level < 4) this.level = 4;
    else if (this.clicks >= 100000 && this.level < 3) this.level = 3;
    else if (this.clicks >= 5000 && this.level < 2) this.level = 2;
    else if (this.clicks >= 1000 && this.level < 1) this.level = 1;

    setInterval(
      function () {
        this.clicks += this.bots.clickBots * this.power * 10;
        this.clicks += this.bots.bigBots * this.power * 100;
        browser.localStorage.setItem("clicker", JSON.stringify(this));
      }.bind(this),
      10000
    );

    setInterval(
      function () {
        for (let tree of this.trees) {
          tree.fruits_nb += tree.trees_nb * this.power;
        }
      }.bind(this),
      30000
    );
  }

  getReward() {
    const availableReward = [];
    for (const reward of rewards) {
      if (reward.minLevel <= this.level || !reward.minLevel) {
        if (reward.maxLevel >= this.level || !reward.maxLevel) {
          availableReward.push(reward);
        }
      }
    }
    return choose(availableReward);
  }

  getTrees() {
    return this.trees.reduce((sum, elem) => sum + elem.trees_nb, 0);
  }

  getFruits() {
    return this.trees.reduce((sum, elem) => sum + elem.fruits_nb, 0);
  }

  increment(inc = 1) {
    this.clicks += inc;
    if (this.clicks >= 1000 && this.level === 0) {
      this.level = 1;
      this.bus.trigger("MILESTONE_1k");
    }
    if (this.clicks >= 5000 && this.level === 1) {
      this.level = 2;
      this.bus.trigger("MILESTONE_5k");
    }
    if (this.clicks >= 100000 && this.level == 2) {
      this.level = 3;
      this.bus.trigger("MILESTONE_100k");
    }
    if (this.clicks >= 1000000 && this.level == 3) {
      this.level = 4;
      this.bus.trigger("MILESTONE_1M");
    }
  }

  buyClickBot() {
    this.bots.clickBots++;
    this.clicks -= 1000;
  }

  buyBigBot() {
    this.bots.bigBots += 1;
    this.clicks -= 5000;
  }

  buyPower() {
    this.power++;
    this.clicks -= 50000;
  }

  buyTree(treeName) {
    for (let tree of this.trees) {
      if (tree.name == treeName) {
        tree.trees_nb += 1;
        this.clicks -= 1000000;
        return;
      }
    }
  }
}
