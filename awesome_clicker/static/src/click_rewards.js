export const rewards = [
    {
       description: "Get 1 click bot",
       apply(clicker) {
             clicker.bots.clickbot.purchased++;
       },
       minLevel: 1,
    },
    {
       description: "Get 10 click bot",
       apply(clicker) {
        clicker.bots.clickbot.purchased += 10;
       },
       minLevel: 3,
       maxLevel: 4,
    },
    {
       description: "Increase bot power!",
       apply(clicker) {
             clicker.multipler += 1;
       },
       minLevel: 3,
    },
 ];