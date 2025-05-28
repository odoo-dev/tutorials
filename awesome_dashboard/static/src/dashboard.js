/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { Layout } from "@web/search/layout";
import { useService } from "@web/core/utils/hooks";
import { DashboardItem } from "./dashboard_item";
import { console };


class AwesomeDashboard extends Component {
    static template = "awesome_dashboard.AwesomeDashboard";
    static components = { Layout, DashboardItem };
    
    setup() {
        this.action = useService("action");
        this.statar = useState([{name: "test", value: 4}]);
        this.statistics = useService("statistics");
        onWillStart(async () =>{
            const statsrpc = await this.statistics.getValue("")
            console.log(statsrpc);
            for (var i in statsrpc) {if (i != "orders_by_size") this.statar.push({name: i, value: statsrpc[i]})};
            console.log("async?");
            console.log(this.statar);
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
