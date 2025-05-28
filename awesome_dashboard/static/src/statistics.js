import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";
import { memoize } from "@web/core/utils/functions";
import console;

const statisticsService = {
    start(env) {
        let state = null;
        const getValue = memoize((key) => {
            if (state === null) state = rpc("/awesome_dashboard/statistics");
            console.log("State is", state);
            if (key === "") return state;
            return state[key];
        })
        return {
            getValue,
        };
    },
};

registry.category("services").add("statistics", statisticsService);
