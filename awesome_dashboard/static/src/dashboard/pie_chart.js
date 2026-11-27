import { Component, useProps, types as t } from "@odoo/owl";
import { useChart } from "./use_chart";


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

    canvasRef = useChart(() => {
        const c_keys = Object.keys(this.props.data);
        const c_data = Object.values(this.props.data);
        const c_color = c_keys.map((key) => SIZE_COLORS[key]);
        return {
            type: "pie",
            data: {
                labels: c_keys,
                datasets: [{
                    label: this.props.label,
                    data: c_data,
                    backgroundColor: c_color,
                }],
            }
        };
    });
}