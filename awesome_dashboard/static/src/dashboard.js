import { Component, onWillStart } from "@odoo/owl";
import { usePlugin, providePlugins} from "@odoo/owl";
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { ActionPlugin } from "@web/webclient/actions/action_plugin";
import { DashboardItem } from "./dashboarditem";
import { ReportingPlugin } from "./reporting_plugin";


class AwesomeDashboard extends Component {
    static components = { Layout, DashboardItem };
    static template = "awesome_dashboard.AwesomeDashboard";
    
    action = usePlugin(ActionPlugin);

    setup() {
        providePlugins([ReportingPlugin]);
        this.reporting = usePlugin(ReportingPlugin);

        onWillStart(() => this.reporting.loadStatistics());
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

registry.category("actions").add("awesome_dashboard.dashboard", AwesomeDashboard);
