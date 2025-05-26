import { registry } from "@web/core/registry";
import { browser } from "@web/core/browser/browser";
import { ClickerModel } from "./clicker_model";
import { CURRENT_VERSION, migrations } from "./migrations";

const LOCAL_STORAGE_KEY = "clicker_game.state";

function migrate(state) {
    let version = state.version || 0;

    while (version < CURRENT_VERSION) {
        const migration = migrations.find(m => m.fromVersion === version);
        if (!migration) break;
        state = migration.apply(state);
        version = migration.toVersion;
        state.version = version;
    }

    return state;
}

function loadState() {
    const raw = browser.localStorage.getItem(LOCAL_STORAGE_KEY);
    if (raw) {
        try {
            const parsed = JSON.parse(raw);
            return migrate(parsed);
        } catch (e) {
            console.warn("Corrupted localStorage state. Ignoring.");
        }
    }
    return null;
}

function saveState(clicker) {
    const data = JSON.stringify(clicker.toJSON());
    browser.localStorage.setItem(LOCAL_STORAGE_KEY, data);
}

let clicker = new ClickerModel();
const restored = loadState();
if (restored) {
    clicker.applyState(restored);
}

// Save state every 10s
setInterval(() => {
    saveState(clicker);
}, 10 * 1000);

registry.category("services").add("awesome_clicker.clicks", {
    start() {
        return { clicker };
    },
});
