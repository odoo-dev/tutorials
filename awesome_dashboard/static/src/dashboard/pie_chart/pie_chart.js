/** @odoo-module **/

import { Component, onMounted, onWillStart, onWillUnmount, useEffect, useRef, xml } from "@odoo/owl";
import { loadJS } from "@web/core/assets";

export class PieChart extends Component {
    static template = xml`
        <canvas t-ref="canvas" width="300" height="300"></canvas>
    `;
    static props = {
        'data': { type: Object}
    }

    setup() {
        this.canvasRef = useRef('canvas');

        onWillStart(() => {
            return loadJS("/web/static/lib/Chart/Chart.js");
        });

        onMounted(() => {
            const ctx = this.canvasRef.el.getContext('2d');
            this.chart = new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: Object.keys(this.props.data),
                    datasets: [{
                        data: Object.values(this.props.data)
                    }]
                },
                options: {}
            });
        });

        useEffect(() => {
            if (this.chart) {
                this.chart.data.labels = Object.keys(this.props.data);
                this.chart.data.datasets[0].data = Object.values(this.props.data);
                this.chart.update();
            }
        }, () => [this.props.data]);

        onWillUnmount(() => {
            this.chart.destroy();
        });
    }
}
