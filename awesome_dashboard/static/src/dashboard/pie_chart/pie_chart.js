/** @odoo-module **/

import {loadJS} from "@web/core/assets"
import {Component, onWillStart, onWillUnmount, useEffect, useRef} from "@odoo/owl";

export class PieChart extends Component {
    static template = "awesome_dashboard.PieChart";

    static props = {
        data: {
            type: Object, optional: true,
        },
    }

    setup() {
        this.chart = null;
        this.canvasRef = useRef("canvas");

        onWillStart(() => loadJS("/web/static/lib/Chart/Chart.js"));
        useEffect(() => this.renderChart());
        onWillUnmount(this.onWillUnmount);
    }

    onWillUnmount() {
        if (this.chart) {
            this.chart.destroy();
        }
    }

    renderChart() {
        if (this.chart) {
            this.chart.destroy();
        }
        this.chart = new Chart(this.canvasRef.el, {
            type: 'pie', data: {
                labels: Object.keys(this.props.data), datasets: [{
                    data: Object.values(this.props.data)
                }]
            }, options: {
                responsive: true, plugins: {
                    legend: {
                        position: 'top',
                    },
                }
            }
        });
    }
}