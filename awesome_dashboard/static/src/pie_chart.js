import { Component, signal, useProps, types as t } from "@odoo/owl";
import { onWillStart, useEffect } from "@odoo/owl";
import { loadJS } from "@web/core/assets";


const SIZE_COLORS = {
    s: "#36A2EB",
    m: "#4BC0C0",
    l: "#ffe37a",
    xl: "#FF9F40",
    xxl: "#FF6384",
};

export class PieChart extends Component {
    static template = "awesome_dashboard.PieChart";

    props = useProps({
        label: t.string(),
        data: t.object(),
    });

    canvasRef = signal.ref();

    setup() {
        onWillStart(() => loadJS("/web/static/lib/Chart/Chart.js"));

        useEffect(() => {
            const canvas = this.canvasRef();
            if (canvas) {
                const chart = this.renderChart(canvas);
                return () => chart.destroy();
            }
        });
    }

    renderChart(canvas) {
        const c_keys = Object.keys(this.props.data);
        const c_data = Object.values(this.props.data);
        const c_color = c_keys.map((key) => SIZE_COLORS[key]);
        return new Chart(canvas, {
            type: "pie",
            data: {
                labels: c_keys,
                datasets: [{
                    label: this.props.label,
                    data: c_data,
                    backgroundColor: c_color,
                }],
            },
        });
    }
}