import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";
import { reactive } from "@odoo/owl";


const dashboardService = {
    start() {
        const result = reactive({ isReady: false });

        setInterval(function() {this.result = rpc("/awesome_dashboard/statistics")}, 600000);

        return {
            loadStatistics() {
                if(this.result in window)
                    this.result = rpc("/awesome_dashboard/statistics");
                return this.result;
            }
        }
    }
};

registry.category("services").add("awesome_dashboard.statistics", dashboardService);
