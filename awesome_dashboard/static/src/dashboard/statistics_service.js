import {registry} from "@web/core/registry";
import {rpc} from "@web/core/network/rpc";
import {reactive} from "@odoo/owl";

export const statisticsService = {
    start() {
        const statistics = reactive({isReady: false, data: {}});

        const loadData = async () => {
            const data = await rpc("/awesome_dashboard/statistics");
            Object.assign(statistics, data, {isReady: true});
        };

        setInterval(loadData, 5 * 1000);
        loadData();

        return statistics;
    },
};

registry.category("services").add("awesome_dashboard.statistics", statisticsService);