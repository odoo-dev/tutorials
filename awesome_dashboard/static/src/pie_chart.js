import { Component, onMounted, onWillUnmount, onWillStart, signal, usePlugin } from "@odoo/owl";
import { loadJS } from "@web/core/assets";
import { ReportingPlugin } from "./reporting_plugin";

export class PieChart extends Component {
	static template = "awesome_dashboard.PieChart";
    canvasRef = signal.ref();
    chart = null;
    config = {
        type: 'pie',
    };

    reporting = usePlugin(ReportingPlugin);
	setup() {
		onWillStart(async () => {
            await this.reporting.loadStatistics();
            return loadJS("/web/static/lib/Chart/Chart.js");
		});
        onMounted(() => {
            this.renderChart();
        });
        onWillUnmount(() => {
            if (this.chart) {
                this.chart.destroy();
            }
        });

        const rep = this.reporting.stats().orders_by_size;

        this.config.data = {
            labels: Object.keys(rep),
            datasets: [{
                label: 'My First Dataset',
                data: Object.values(rep),
                backgroundColor: [
                    'rgb(255, 99, 132)',
                    'rgb(54, 162, 235)',
                    'rgb(255, 205, 86)'
                ],
                hoverOffset: 4
            }]
        };
	}

    renderChart() {
        this.chart = new Chart(this.canvasRef(), this.config);
    }
}
