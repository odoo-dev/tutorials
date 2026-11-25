import { Plugin, signal } from "@odoo/owl";
import { services } from "@web/core/services";
import { rpc } from "@web/core/network/rpc";

export class ReportingPlugin extends Plugin{
    statistics = signal(null);

    async loadStatistics() {
        const data = await rpc("/awesome_dashboard/statistics", {}, {cache: true});
        this.statistics.set(data);
    }

}

services.add(ReportingPlugin);
