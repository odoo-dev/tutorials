import { EventBus } from "@odoo/owl";
import { useState, useEffect } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export function useClicker() {
    const clicker = useService("awesome_clicker.clicks");
    const bus = new EventBus();
    const effectService = useService("effect");
    bus.addEventListener("MILESTONE_1k", notify);

    function notify() {
        effectService.add({
            type: "rainbow_man",
            message: "Milestone reached! You can now buy clickbots",
        });
    }

    let clicks = useState(clicker.clicker.clicks);
    let levels = useState(clicker.clicker.levels);
    let clickBots = useState(clicker.clicker.clickBots);
    let bigClickBots = useState(clicker.clicker.bigClickBots);
    let powerMultiplier = useState(clicker.clicker.powerMultiplier);
    let pearsTree = useState(clicker.clicker.pearsTree);
    let cherriesTree = useState(clicker.clicker.cherriesTree);
    let peachesTree = useState(clicker.clicker.peachesTree);
    let pears = useState(clicker.clicker.pears);
    let cherries = useState(clicker.clicker.cherries);
    let peaches = useState(clicker.clicker.peaches);

    const levelUp = () => {
        levels.level += 1;
    };

    useEffect(() => {
        if (levels.level === 0 && clicks.count >= 1000) {
            levelUp();
            bus.trigger("MILESTONE_1k");
        } else if (levels.level === 1 && clicks.count >= 5000) {
            levelUp();
        } else if (levels.level === 2 && clicks.count >= 100000 && powerMultiplier.multiplier === 1) {
            levelUp();
        } else if (levels.level === 3 && clicks.count >= 1000000) {
            levelUp();
        }
    }, () => [clicks.count]);

    setInterval(() => {
        clicks.count += ((10 * clickBots.bots * powerMultiplier.multiplier) + (100 * bigClickBots.bots))
    }, 10 * 1000);

    setInterval(()=>{
        pears.count += 1 * pearsTree.tree;
        cherries.count += 1 * cherriesTree.tree;
        peaches.count += 1 * peachesTree.tree;
    }, 30 * 1000);

    const increment = () => {
        clicks.count += 10;
    };

    const buyClickBot = () => {
        clicks.count -= 1000;
        clickBots.bots += 1;
    };

    const buyBigClickBot = () => {
        clicks.count -= 5000;
        bigClickBots.bots += 1;
    }

    const buyPowerMultiplier = () => {
        clicks.count -= 50000;
        powerMultiplier.multiplier += 1;
    }

    const buyPearsTree = () => {
        clicks.count -= 1000000;
        pearsTree.tree += 1;
    }

    const buyCherriesTree = () => {
        clicks.count -= 1000000;
        cherriesTree.tree += 1;
    }

    const buyPeachesTree = () => {
        clicks.count -= 1000000;
        peachesTree.tree += 1;
    }

    return {
        clicks: clicks,
        levels: levels,
        clickBots: clickBots,
        bigClickBots: bigClickBots,
        powerMultiplier: powerMultiplier,
        pearsTree: pearsTree.tree,
        cherriesTree: cherriesTree.tree,
        peachesTree: peachesTree.tree,
        pears: pears.count,
        cherries: cherries.count,
        peaches: peaches.count,
        increment: increment,
        buyClickBot: buyClickBot,
        buyBigClickBot: buyBigClickBot,
        buyPowerMultiplier: buyPowerMultiplier,
        buyPearsTree: buyPearsTree,
        buyCherriesTree: buyCherriesTree,
        buyPeachesTree: buyPeachesTree,
    };
}

/**
 * Choose a random element from an array.
 * @param {Array} array
 * @returns {*} A random element from the array
 */
export function choose(array) {
    if (!array.length) return null;
    const index = Math.floor(Math.random() * array.length);
    return array[index];
}
