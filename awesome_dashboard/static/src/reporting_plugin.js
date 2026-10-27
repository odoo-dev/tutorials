import { Plugin, signal } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";
import { services } from "@web/core/services";

export class ReportingPlugin extends Plugin {
    stats = signal({});

    async loadStatistics() {
        return this.stats.set(await rpc("/awesome_dashboard/statistics", {}, { cache: true }));
    }
}
services.add(ReportingPlugin);
