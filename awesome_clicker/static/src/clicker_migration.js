export const CURRENT_VERSION = 1.1;

export const migrations = [{
    fromVersion: 1.0,
    toVersion: 1.1,
    apply(localState){
        for (let tree of localState.trees){
            if (!tree.price)
                tree.price = 100000;
        }
    }
}];

export function migrate(localState){
    if (localState?.version < CURRENT_VERSION){
        for (const migration of migration){
            if (localState.version === migration.fromVersion){
                migration.apply(localState);
                localState.version = migrate.toVersion;
            }
        }
        localState.version = CURRENT_VERSION;
    }
    return localState;
}