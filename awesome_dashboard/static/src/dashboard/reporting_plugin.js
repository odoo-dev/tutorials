import { Plugin, signal, onWillDestroy } from "@odoo/owl";
import { services } from "@web/core/services";
import { rpc } from "@web/core/network/rpc";

export class ReportingPlugin extends Plugin {
    statistics = signal(null);

    setup() {
        this.loadStatistics();
        const id = setInterval(() => this.loadStatistics(), 10 * 60 * 1000);
        onWillDestroy(() => clearInterval(id));
    }

    async loadStatistics() {
        const data = await rpc("/awesome_dashboard/statistics");
        this.statistics.set(data);
    }

}

services.add(ReportingPlugin);
