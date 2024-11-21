/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { useService } from "@web/core/utils/hooks";
import { AwesomeDashboardItem } from "./dashboard_item";
import { PieChart } from "./pie_chart/pie_chart";

class AwesomeDashboard extends Component {
    static template = "awesome_dashboard.AwesomeDashboard";
    static components = { Layout, AwesomeDashboardItem, PieChart };

    async setup() {
        this.action = useService("action");
        this.data = useState(useService("awesome_dashboard.statistics"));
        this.items = registry.category("awesome_dashboard").getAll();
    }
    openCustomerView() {
        this.action.doAction(
            "base.action_partner_form"
        );
    }
    openLeads() {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "crm.lead",
            views: [[false, "list"], [false, "form"]],
            target: 'current',
        });
    }
}

registry.category("lazy_components").add("AwesomeDashboard", AwesomeDashboard);
