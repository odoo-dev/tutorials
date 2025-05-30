/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { useService } from "@web/core/utils/hooks";
import { DashboardItem } from "./dashboard_item";
import { console };
import { PieChart } from "./pie_chart"

class AwesomeDashboard extends Component {
    static template = "awesome_dashboard.AwesomeDashboard";
    static components = { Layout, DashboardItem, PieChart };
    
    setup() {
        this.action = useService("action");
        this.statar = useState({ar: [{name: "test", value: 4}]});
        this.statistics = useService("statistics");
        onWillStart(async () =>{
            const statsrpc = await this.statistics.getValue("")
            console.log("rpc:",statsrpc);
            for (var i in statsrpc) {if (i != "orders_by_size") this.statar.ar.push(statsrpc[i])};
            console.log("async?");
            console.log(this.statar);
            this.statistics.getValue("nb_new_orders");
        })
        
    }
    
    openCustomers(){
        this.action.doAction("base.action_partner_form");
    }
    
    openLeads(){
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Leads',
            res_model: 'crm.lead',
            views: [[false, 'list'], [false, 'form']],
            search_view_id: [false],
        });
    }
}

registry.category("actions").add("awesome_dashboard.dashboard", AwesomeDashboard);
