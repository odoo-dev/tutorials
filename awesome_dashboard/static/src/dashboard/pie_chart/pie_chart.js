import { Component, onWillStart, onMounted, useRef } from "@odoo/owl"
import { loadJS } from "@web/core/assets"


export class PieChart extends Component {
    static template = "awesome_dashboard.pie_chart.pie_chart"
    static props = ['data']

    setup() {
        this.chart = null
        this.pieChart = useRef('pie-chart')

        onWillStart(() => loadJS('/web/static/lib/Chart/Chart.js'))
        onMounted(this.renderChart)
    }

    renderChart() {
        this.chart = new Chart(this.pieChart.el, {
            type: "pie",
            data: {
                labels: [...Object.keys(this.props.data)],
                datasets: [
                    {
                        data: [...Object.values(this.props.data)],
                    },
                ],
            }
        })
    }
}
