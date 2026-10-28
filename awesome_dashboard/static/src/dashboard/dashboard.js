import { Component, usePlugin } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { ActionPlugin } from "@web/webclient/actions/action_plugin";
import { DashboardItem } from "./dashboard_item";
import { ReportingPlugin } from "./reporting_plugin";
import { PieChart } from "./pie_chart";

class AwesomeDashboard extends Component {
    static template = "awesome_dashboard.AwesomeDashboard";
    static components = { Layout, DashboardItem, PieChart };

    action = usePlugin(ActionPlugin);
    openCustomerView() {
        this.action.doAction("base.action_partner_form");
    }

    openLeads() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Leads",
            res_model: "crm.lead",
            views: [[false, "list"], [false, "form"]],
            domain: [["type", "=", "lead"]],
        });
    }

    reporting = usePlugin(ReportingPlugin);
}

registry.category("lazy_components").add("AwesomeDashboard", AwesomeDashboard);
registry.category("actions").add("AwesomeDashboard", AwesomeDashboard);
