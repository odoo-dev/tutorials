import { Plugin, signal } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";


export class ReportingPlugin extends Plugin {

    statistics = signal(null);

    async loadStatistics() {
        // async method returns a Promise, which is needed by onWillStart
        // Cache result by URL and parameters
        const data = await rpc("/awesome_dashboard/statistics", {}, { cache: true });
        this.statistics.set(data);
    }
}
