export const rewards = [
    {
        description: "Get 1 free click",
        apply(clicker) {
            clicker.increment(1);
        },
        maxLevel: 3,
    },
    {
        description: "Get 10 free click",
        apply(clicker) {
            clicker.increment(10);
        },
        minLevel: 3,
        maxLevel: 4,
    },
    {
        description: "Free power upgrade",
        apply(clicker) {
            clicker.power++;
        },
        minLevel: 3,
    },
];
