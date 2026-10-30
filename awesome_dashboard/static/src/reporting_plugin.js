import { onWillDestroy, Plugin, signal } from "@odoo/owl";
import { services } from "@web/core/services";
import { rpc } from "@web/core/network/rpc";

export class ReportingPlugin extends Plugin {
    reload_per_seconds = 10 * 60;  // 10 minutes
    stats = signal(null);
    stats_label = {
        "average_quantity": "Average amount of t-shirt by order this month",
        "average_time": "Average time for an order to go from 'new' to 'sent' or 'cancelled'",
        "nb_new_orders": "Number of new orders this month",
        "nb_cancelled_orders": "Number of cancelled orders this month",
        "orders_by_size": "Shirt orders by size",
        "total_amount": "Total amount of new orders this month"
    };

    setup() {
        this.loadStatisticsOnce();
        const timer = setInterval(() => {
            this.loadStatisticsOnce();
        }, this.reload_per_seconds * 1000
        );
        onWillDestroy(() => {
            clearInterval(timer);
        });
    }

    async loadStatisticsOnce() {
        const data = await rpc("/awesome_dashboard/statistics");
        this.stats.set(data);
    }
}

services.add(ReportingPlugin);
