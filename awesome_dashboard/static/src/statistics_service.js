import {rpc} from "@web/core/network/rpc";
import {registry} from "@web/core/registry"

async function loadStatistics() {
    console.log("fetching ")
    const result = await rpc("/awesome_dashboard/statistics")
    console.log(result)
    return result;
}

export const statisticsService = {
    start(env) {
        let state = {}
        return {
            loadStatistics
        }
    }

}

registry.category("services").add("awesome_owl.statistics", statisticsService);