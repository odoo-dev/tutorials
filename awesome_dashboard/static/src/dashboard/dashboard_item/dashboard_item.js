/** @odoo-module **/

import {Component} from "@odoo/owl";

export class DashboardItem extends Component {
    static template = "awesome_dashboard.DashboardItem";

    static props = {
        slots: {type: Object, optional: true, validate: slots => "default" in slots},
        size: {type: Number, default: 1, optional: true}
    }
}