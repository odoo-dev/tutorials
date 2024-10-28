import { Component } from "@odoo/owl";


export default class DashboardItem extends Component {
    static props = {
        size: {type: Number, optional: true},
        text: {type: String},
        content: {type: Object}
    };

    setup() {
        this.test = typeof this.props.content;
    }

    static template = "awesome_dashboard.DashboardItem";
}
