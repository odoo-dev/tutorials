import { choose } from "../utils.js";

export const rewards = [
   {
      description: "Get 1 click bot",
      apply(clicker) {
            clicker.increment();
      },
      maxLevel: 3,
   },
   {
      description: "Get 10 click bot",
      apply(clicker) {
            clicker.increment();
      },
      minLevel: 3,
      maxLevel: 4,
   },
   {
      description: "Increase bot power!",
      apply(clicker) {
            clicker.powerMultiplier.multipler += 1;
      },
      minLevel: 3,
   },
];

export function getReward(currentLevel) {
    const availableRewards = rewards.filter((reward) => {
        return (
            (reward.minLevel === undefined || currentLevel >= reward.minLevel) &&
            (reward.maxLevel === undefined || currentLevel <= reward.maxLevel)
        );
    });
    return choose(availableRewards);
}