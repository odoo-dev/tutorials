export const CURRENT_VERSION = 2;

export const migrations = [
    {
        fromVersion: 1,
        toVersion: 2,
        apply(state) {
            state.peachesTree = { tree: 0 };
            state.peaches = { count: 0 };
            state.version = 2;
            return state;
        },
    },
];
