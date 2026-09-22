import {rpc} from "@web/core/network/rpc";
import {registry} from "@web/core/registry"
import {memoize} from "@web/core/utils/functions"

async function loadStatistics() {
    const result = await rpc("/awesome_dashboard/statistics");
    return result;
}

export const statisticsService = {
    start(env) {
        return {
            loadStatistics: memoize(loadStatistics)
        }
    }

}

registry.category("services").add("awesome_owl.statistics", statisticsService);