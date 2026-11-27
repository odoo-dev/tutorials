import { Plugin, signal, onWillDestroy } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";


export class ReportingPlugin extends Plugin {

    statistics = signal(null);

    async loadStatistics() {
        // async method returns a Promise, which is needed by onWillStart
        // Cache result by URL and parameters
        const data = await rpc("/awesome_dashboard/statistics");
        this.statistics.set(data);
    }

    setup() {
        this.loadStatistics();
        const intervalId = setInterval(() => this.loadStatistics(), 3 * 1000);

        onWillDestroy(() => clearInterval(intervalId));
    }
}
