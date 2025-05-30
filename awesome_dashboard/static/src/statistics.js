import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";
import { memoize } from "@web/core/utils/functions";
import console;
import { reactive, toRaw } from "@odoo/owl";


const statisticsService = {
    start(env) {
        let state = reactive({values: {}});
        let intervalId = null;
        console.log("Start state is", state);
        const refreshState = async () => {
            const request = await rpc("/awesome_dashboard/statistics");
            for (var i in request) {
                //console.log("appending", i, request[i]);
                if (!state.values[i]) state.values[i] = {name: i};
                if (typeof request[i] === "object")
                {
                    if(!(state.values[i].value)) state.values[i].value = {};
                    for (var oldprop in state.values[i].value) delete state.values[i].value[oldprop];
                    for (var newprop in request[i]) state.values[i].value[newprop] = request[i][newprop];
                    console.log(i," is object")
                }
                if (!(typeof request[i] === "object")) state.values[i].value = request[i];
                //console.log("after append", i, "state is", toRaw(state))
            }
            console.log("refreshed state is",state);
            setTimeout(refreshState, 10000);
        }
        
        const getValue = memoize(async (key) => {
            console.log("fetching key", key);
            if (Object.keys(state.values).length === 0) {await refreshState();}
            console.log("State is", state);
            console.log("State values is", state.values);
            if (key === "") return state.values;
            console.log("key is", key);
            console.log("State value is", state.values[key]);
            //for (var i in state.values) console.log(i);
            return state.values[key];
        });
        return {
            getValue,
        };
    },
};

registry.category("services").add("statistics", statisticsService);
