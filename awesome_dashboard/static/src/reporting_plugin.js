import { Plugin, signal } from "@odoo/owl";
import { services } from "@web/core/services";
import { rpc } from "@web/core/network/rpc";

export class ReportingPlugin extends Plugin {
    stats = signal({});
    stats_label = {
        "average_quantity": "Average amount of t-shirt by order this month",
        "average_time": "Average time for an order to go from 'new' to 'sent' or 'cancelled'",
        "nb_new_orders": "Number of new orders this month",
        "nb_cancelled_orders": "Number of cancelled orders this month",
        "orders_by_size": "Shirt orders by size",
        "total_amount": "Total amount of new orders this month"
    };

    async loadStatistics() {
        const data = await rpc("/awesome_dashboard/statistics", {}, { cache: true });
        this.stats.set(data);
    }
}

services.add(ReportingPlugin);
