/** @odoo-module **/

import { Component, onWillStart, reactive, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { DashboardItem } from "./DashboardItem";
import { PieChart } from "./piechart";


class LazyDashboard extends Component {
    static template = "awesome_dashboard.LazyDashboard";

    setup() {
        this.statistics = useState(useService("awesome_dashboard.statistics"));   
        
        this.action = useService("action");
    }

    openCustomers() {
        this.action.doAction("base.action_partner_form");
    }
    
    openLeads() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: _t('Leads'),
            target: 'current',
            res_model: 'crm.lead',
            views: [[false, 'list'], [false, 'form']],
        });
    }

    static components = { Layout, DashboardItem, PieChart };
}

registry.category("lazy_components").add("awesome_dashboard.LazyDashboard", LazyDashboard);
