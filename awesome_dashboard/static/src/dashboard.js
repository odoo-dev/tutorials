import {Component, onWillStart, useState} from "@odoo/owl";
import {_t} from "@web/core/l10n/translation";

import {registry} from "@web/core/registry";
import {Layout} from "@web/search/layout";
import {useService} from "@web/core/utils/hooks";
import {DashboardItem} from "./DashboardItem";
import {PieChart} from "./PieChart";

//     "result": {
//         "average_quantity": 7,
//         "average_time": 6,
//         "nb_cancelled_orders": 6,
//         "nb_new_orders": 174,
//         "orders_by_size": {
//             "m": 14,
//             "s": 4,
//             "xl": 118
//         },
//         "total_amount": 117
//     }


class AwesomeDashboard extends Component {
    static template = "awesome_dashboard.AwesomeDashboard";
    static components = {Layout, DashboardItem, PieChart};


    setup() {
        this.action = useService("action");
        this.state = useState({stats: {}})
        this.stats = useService("awesome_owl.statistics");
        console.log(this.stats)
        //
        // onWillStart(async () => {
        //     // console.log('abc')
        //     this.state.stats = await this.stats.loadStatistics().resp;
        //     console.log('state', this.state)
        // })

    }

    openCustomer() {
        this.action.doAction("base.action_partner_form");
    }

    async openLeads(activity) {
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: _t('Leads'),
            res_model: 'crm.lead',
            views: [[false, 'list'], [false, 'form']],
        });
    }
}

registry.category("actions").add("awesome_dashboard.dashboard", AwesomeDashboard);
