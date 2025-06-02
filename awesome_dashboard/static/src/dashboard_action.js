/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { LazyDashboard } from "./dashboard/dashboard";
import { LazyComponent } from "@web/core/assets";
import { DashboardBundle } from "./dashboard/dashboardBundle"

class AwesomeDashboard extends Component {
    static template = "awesome_dashboard.AwesomeDashboard";

    static components = { LazyComponent, LazyDashboard, DashboardBundle };
}

registry.category("actions").add("awesome_dashboard.dashboard", AwesomeDashboard);

