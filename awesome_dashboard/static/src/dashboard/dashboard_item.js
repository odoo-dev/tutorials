/** @odoo-module **/

import { Component, useState } from "@odoo/owl";

export class DashboardItem extends Component {
    static template = "awesome_dashboard.DashboardItem";

    static props = {
        slots: { type: Object },
        size: { type: Number , optional: true, default: 1},
    };
}
