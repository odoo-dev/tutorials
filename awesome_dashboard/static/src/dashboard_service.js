import { registry } from "@web/core/registry";
import { memoize } from "@web/core/utils/functions";
import { rpc } from "@web/core/network/rpc";

export const dashboardService = {
    start(env) {
        return {
            loadStatistics: memoize(() => rpc("/awesome_dashboard/statistics")),
        };
    },
};

registry.category("services").add("awesome_dashboard.statistics", dashboardService);
