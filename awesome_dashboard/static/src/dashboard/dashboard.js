import { Component } from "@odoo/owl";
import { usePlugin, providePlugins} from "@odoo/owl";
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { ActionPlugin } from "@web/webclient/actions/action_plugin";
import { DashboardItem } from "./dashboarditem";
import { dashboardItems } from "./dashboard_items";
import { ReportingPlugin } from "./reporting_plugin";
import { PieChart } from "../pie_chart/pie_chart";


class AwesomeDashboard extends Component {
    static components = { Layout, DashboardItem, PieChart };
    static template = "awesome_dashboard.AwesomeDashboard";
    
    action = usePlugin(ActionPlugin);

    items = dashboardItems.items;

    setup() {
        providePlugins([ReportingPlugin]);
        this.reporting = usePlugin(ReportingPlugin);
    }

    openCustomersView() {
        this.action.doAction("base.action_partner_form");
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

registry.category("lazy_components").add("AwesomeDashboard", AwesomeDashboard);
