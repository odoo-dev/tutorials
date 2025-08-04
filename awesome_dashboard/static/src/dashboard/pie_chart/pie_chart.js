import { Component, onWillStart, onMounted, onWillUnmount, onWillUpdateProps, useRef } from "@odoo/owl";
import { getColor } from "@web/core/colors/colors";
import { loadJS } from "@web/core/assets";

export class PieChart extends Component {
    static template = "awesome_dashboard.PieChart";
    static props = {
        label: { type: String },
        data: { type: Object },
    };

    setup() {
        this.canvasRef = useRef("canvas");
        onWillStart(() => loadJS("/web/static/lib/Chart/Chart.js"));
        onMounted(() => this.renderChart());
        onWillUnmount(() => this.chart.destroy());
        onWillUpdateProps((nextProps) => {
            if (this.chart && nextProps.data !== this.props.data) {
                this.updateChart(nextProps.data);
            }
        });
    }

    renderChart() {
        const labels = Object.keys(this.props.data);
        const data = Object.values(this.props.data);
        const color = labels.map((_, index) => getColor(index));
        this.chart = new Chart(this.canvasRef.el, {
            type: "pie",
            data: {
                labels: labels,
                datasets: [
                    {
                        label: this.props.label,
                        data: data,
                        backgroundColor: color,
                    },
                ],
            },
        });
    }

    updateChart(newData) {
        const labels = Object.keys(newData);
        const data = Object.values(newData);
        const colors = labels.map((_, index) => getColor(index));

        this.chart.data.labels = labels;
        this.chart.data.datasets[0].data = data;
        this.chart.data.datasets[0].backgroundColor = colors;
        this.chart.update("active"); // 'none' for no animation, or 'active' for smooth transition
    }
}
