import { Component } from "@odoo/owl";
import PieChart from  "./piechart"


export default class PieChartCard extends Component {
    static props = {
        size: {type: Number, optional: true},
        text: String,
        content: Object,
    };

    static template = "awesome_dashboard.PieChartCard";

    static components = {PieChart}
}
