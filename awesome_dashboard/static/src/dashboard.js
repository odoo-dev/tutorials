import { Component, onWillStart, signal, usePlugin } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { ActionPlugin } from "@web/webclient/actions/action_plugin";
import { DashboardItem } from "./dashboard_item";
import { ReportingPlugin } from "./reporting_plugin";

class AwesomeDashboard extends Component {
    static template = "awesome_dashboard.AwesomeDashboard";
    static components = { Layout, DashboardItem };

    action = usePlugin(ActionPlugin);
    reporting = usePlugin(ReportingPlugin);

    stats = signal({});
    stats_label = {
        "average_quantity": "Average amount of t-shirt by order this month",
        "average_time": "Average time for an order to go from 'new' to 'sent' or 'cancelled'",
        "nb_new_orders": "Number of new orders this month",
        "nb_cancelled_orders": "Number of cancelled orders this month",
        "total_amount": "Total amount of new orders this month"
    };

    setup() {
        onWillStart(async () => {
            const data = await this.reporting.loadStatistics();
            this.stats.set(data);
        });
    }

    openCustomerView() {
        this.action.doAction("base.action_partner_form")
    }

    openLeads() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "All leads",
            res_model: "crm.lead",
            views: [
                [false, "list"],
                [false, "form"],
            ],
        });
    }
}

registry.category("actions").add("awesome_dashboard.dashboard", AwesomeDashboard);
