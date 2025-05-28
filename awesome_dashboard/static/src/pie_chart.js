import { Component } from "@odoo/owl";
import { Layout } from "@web/search/layout";


export class PieChart extends Component {
    static template = "awesome_dashboard.PieChart";
    this.chart = null
    this.statObject = null
    
    setup() {
        this.statistics = useService("statistics");
        
        onWillStart(() => {
            this.chart = loadJs("/web/static/lib/Chart/Chart.js");
            console.log("loaded chart");
        });
        
        onWillStart(async () => {
            const reply = await this.statistics.getValue("orders_by_size");
            
        })
    }
}
