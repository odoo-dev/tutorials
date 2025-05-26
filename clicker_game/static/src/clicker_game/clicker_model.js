import { Reactive } from "@web/core/utils/reactive";
import { CURRENT_VERSION } from "./migrations";

export class ClickerModel extends Reactive {
    constructor() {
        super();
        this.clicks = { count: 0 };
        this.levels = { level: 0 };
        this.clickBots = { bots: 0 };
        this.bigClickBots = { bots: 0 };
        this.powerMultiplier = { multiplier: 1 };
        this.pearsTree = { tree: 0 };
        this.cherriesTree = { tree: 0 };
        this.peachesTree= { tree: 0 },
        this.pears = { count: 0 };
        this.cherries = { count: 0 };
        this.peaches = { count: 0 };
    }

    toJSON() {
        return {
            version: CURRENT_VERSION,
            clicks: this.clicks,
            levels: this.levels,
            clickBots: this.clickBots,
            bigClickBots: this.bigClickBots,
            powerMultiplier: this.powerMultiplier,
            pearsTree: this.pearsTree,
            cherriesTree: this.cherriesTree,
            peachesTree: this.peachesTree,
            pears: this.pears,
            cherries: this.cherries,
            peaches: this.peaches,
        };
    }

    applyState(state) {
        Object.assign(this, state);
    }
}
