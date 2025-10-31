import { Component } from "@odoo/owl"


export class DashboardItem extends Component {
    static template = "awesome_dashboard.item.item"
    static props = {
        slot: {
            type: Object,
            shape: {
                default: {}
            }
        },
        size: {
            type: Number,
        }
    }
}
