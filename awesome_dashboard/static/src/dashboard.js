import { Component, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { useService } from "@web/core/utils/hooks";
import { DashboardItem } from "./dashboard_item";
import { PieChart } from "./pie_chart";

class AwesomeDashboard extends Component {
    static template = "awesome_dashboard.AwesomeDashboard";
    static components = { DashboardItem, Layout, PieChart };

    setup() {
        this.actionService = useService("action");
        this.statisticsService = useService("awesome_dashboard.statistics");
        this.statistics = [];
        this.ordersBySize = {};

        onWillStart(async () => {
            const statistics = await this.statisticsService.loadStatistics();
            this.statistics = statistics.cards;
            this.ordersBySize = statistics.orders_by_size;
        });
    }

    openCustomers() {
        this.actionService.doAction("base.action_partner_customer_form");
    }

    openLeads() {
        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: "Leads",
            res_model: "crm.lead",
            views: [
                [false, "list"],
                [false, "form"],
            ],
        });
    }
}

registry.category("actions").add("awesome_dashboard.dashboard", AwesomeDashboard);
