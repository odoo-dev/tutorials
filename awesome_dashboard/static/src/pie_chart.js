import { Component, onWillStart, useRef, useEffect, useState, onMounted, toRaw } from "@odoo/owl";
import { Layout } from "@web/search/layout";
import { useService } from "@web/core/utils/hooks";
import { loadJS } from "@web/core/assets";


export class PieChart extends Component {
    static template = "awesome_dashboard.PieChart";
    
    setup() {
        this.statistics = useService("statistics");
        this.chart = null;
        this.statObject = useState({stats: null});
        this.canvasRef = useRef("chartCanvas");
        onWillStart(async () => {
            await loadJS("/web/static/lib/Chart/Chart.js");
            console.log("loaded chart", Chart);
        });
        
        onWillStart(async () => {
            const reply = await this.statistics.getValue("orders_by_size");
            console.log("got reply", reply)
            this.statObject.stats = reply;
            console.log("got stats", this.statObject);
        })
        
      useEffect(() => this.renderChart());
    }
    
    renderChart() {
        if (this.chart) {
            this.chart.destroy();
        }
        console.log("renderer called");
        console.log(this.statObject);
        if (Chart) console.log(Chart);
        const data = {};
        if ((this.statObject.stats.value)&&(Chart)&&(this.canvasRef.el)) {
            const options = {};
            data.datasets = [];
            data.labels = [];
            data.datasets.push({
                label: "size",
                data: [this.statObject.stats.value.m, this.statObject.stats.value.s, this.statObject.stats.value.xl],
            });
            data.labels.push("m", "s", "xl");
            this.chart = new Chart(this.canvasRef.el, {data, options, type: "pie"} );
            console.log("data is", data);
            console.log("rendered chart");
        }
    }
}
