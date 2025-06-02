import { rpc } from "@web/core/network/rpc";
import { memoize } from "@web/core/utils/functions";
import { registry } from "@web/core/registry";
import { reactive } from "@odoo/owl";


async function loadStatistics() {
    return await rpc("/awesome_dashboard/statistics")
}

const statistics = {
    
    start() {

        let loadStatisticsMemoized = reactive({data: null});
    
        
        async function fetch_data() {
            setTimeout(() => {
                fetch_data();
            }, 10000);
            loadStatisticsMemoized.data = await loadStatistics();

        };

        fetch_data();
        
        return {
            loadStatisticsMemoized
        };
    }
};

registry.category("services").add("awesome_dashboard.statistics", statistics);
