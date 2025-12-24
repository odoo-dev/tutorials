export const CURRENT_VERSION = 2.0;
export const migrations = [
    {
        fromVersion: 1.0,
        toVersion: 2.0,
        apply: (state) => {
            state.trees.peachTree = {
                price: 1500000,
                level: 5,
                produce: 'peach',
                purchased: 0,
            };
            state.fruits.peach = 0;
        },
    },
];

export function migrate(localState) {
    console.log("Migration started")
    if (localState?.version < CURRENT_VERSION) {
        console.log("Current save version: " + localState.version);
        for (const migration of migrations) {
            console.log("Checking migration from " + migration.fromVersion + " to " + migration.toVersion);
            if (localState.version === migration.fromVersion){
                console.log("Applying migration");
                migration.apply(localState);
                console.log("Updating save version");
                localState.version = migration.toVersion;
                console.log("Update completed");
            }
        }
    }
    console.log("LocalState updated");
    console.log(localState);
    return localState;
}
