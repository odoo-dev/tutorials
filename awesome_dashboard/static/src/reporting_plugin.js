import { Plugin } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";


export class ReportingPlugin extends Plugin {

    loadStatistics() {
        // Cach result by URL and parameters
        return rpc("/awesome_dashboard/statistics", {}, { cache: true });
    }
}
