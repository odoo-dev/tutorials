/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { Component, xml, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { useService } from "@web/core/utils/hooks";
import DashboardItem from  "./dashboarditem"
import PieChartCard from  "./piechartcard"

class AwesomeDashboard extends Component {
    static template = xml`
        <button class="btn btn-primary" t-on-click="openCustomers">
            Customers
        </button>
        <button class="btn btn-primary" t-on-click="openLeads">
            Leads
        </button>
        <Layout className="'o_dashboard h-100'" display="{controlPanel: {} }">
            <t t-foreach="items" t-as="item" t-key="item.id">
                <DashboardItem text="item.text" content="item.content" size="item.size"/>
            </t>
            <PieChartCard label="'TEST'" data="result.orders_by_size" size="2"/>
        </Layout>`;

    static components = {Layout, DashboardItem, PieChartCard}

    setup() {
        this.openCustomersAction = useService("action");
        this.openLeadsActions = useService("action");

        this.statisticsService = useService("awesome_dashboard.statistics");

        onWillStart(async () => {
            this.result = await this.statisticsService.loadStatistics();
    
            this.initializeItems(this.result);
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

    initializeItems(result) {
        this.items = [
            {
                id: "average_quantity",
                description: "Average quantity desc",
                size: 1,
                text: "Average quantity",
                content: result.average_quantity
            },
            {
                id: "average_time",
                description: "Average time desc",
                size: 1,
                text: "Average time",
                content: result.average_time
            },
            {
                id: "new_orders",
                description: "New orders desc",
                size: 1,
                text: "New orders",
                content: result.nb_new_orders
            },
            {
                id: "cancelled_orders",
                description: "Cancelled orders desc",
                size: 1,
                text: "Cancelled orders",
                content: result.nb_cancelled_orders
            },
            {
                id: "total_orders",
                description: "Total orders desc",
                size: 2,
                text: "Total orders",
                content: result.total_amount
            }
        ];
    }
}

registry.category("lazy_components").add("awesome_dashboard.dashboard", AwesomeDashboard);
