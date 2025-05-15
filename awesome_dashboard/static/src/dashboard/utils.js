import { reactive } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";
import { registry } from "@web/core/registry";
import { memoize } from "@web/core/utils/functions";

// const loadStatistics = memoize(async () => {
//     return await rpc("/awesome_dashboard/statistics");
// });

export const statisticService = {
    start() {
        const state = reactive({ data: {} });

        async function reload() {
            const res = await rpc("/awesome_dashboard/statistics");
            Object.assign(state.data, res);
        }

        setInterval(reload, 10 * 1000);
        reload();

        return {
            state,
            // loadStatistics
        };
    }
}

registry.category("services").add("awesome_dashboard.statistic", statisticService);
