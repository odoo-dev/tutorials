/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { Component, xml, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { useService } from "@web/core/utils/hooks";
import DashboardItem from  "./dashboarditem"

class AwesomeDashboard extends Component {
    static template = xml`
        <button class="btn btn-primary" t-on-click="openCustomers">
            Customers
        </button>
        <button class="btn btn-primary" t-on-click="openLeads">
            Leads
        </button>
        <Layout className="'o_dashboard h-100'" display="{controlPanel: {} }">
            <DashboardItem text="'Average amount'" content="this.result.average_quantity"/>
            <DashboardItem text="'Average time'" content="this.result.average_time" size="2"/>
            <DashboardItem text="'New orders'" content="this.result.nb_new_orders"/>
            <DashboardItem text="'Cancelled orders'" content="this.result.nb_cancelled_orders"/>
            <DashboardItem text="'Total orders'" content="this.result.total_amount"/>
        </Layout>`;

    static components = {Layout, DashboardItem}

    setup() {
        this.openCustomersAction = useService("action");
        this.openLeadsActions = useService("action");

        this.statisticsService = useService("awesome_dashboard.statistics");

        onWillStart(async () => {
            this.result = await this.statisticsService.getData();
        });
    }

    openCustomers() {
        this.openCustomersAction.doAction({
            type: 'ir.actions.act_window',
            name: _t('Customers'),
            res_model: 'res.partner',
            views: [[false, 'kanban']],
        });
    }

    openLeads() {
        this.openCustomersAction.doAction({
            type: 'ir.actions.act_window',
            name: _t('Leads'),
            res_model: 'crm.lead',
            views: [[false, 'list'], [false, 'form']],
        });
    }
}

registry.category("actions").add("awesome_dashboard.dashboard", AwesomeDashboard);
