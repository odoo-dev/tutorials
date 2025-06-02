import { Component, onWillStart, useRef, onMounted } from "@odoo/owl";
import { loadJS } from "@web/core/assets"

export class PieChart extends Component {
    static template = "awesome_dashboard.PieChart";

    setup() {
        this.canvas_ref = useRef('canvas-ref');

        onMounted(() => {
            new Chart(this.canvas_ref.el.getContext('2d'), {
                type: 'pie',
                data: {
                    labels: Object.keys(this.props.data),
                    datasets: [{
                        label: 'Shirt orders by size',
                        data: Object.values(this.props.data)
                    }]
                }
            });
        });

        onWillStart(async () => {
            await loadJS("/web/static/lib/Chart/Chart.js");
        })
    }

    static props = {
        data : {type : Object},        
    }
}
