import { Component, onWillStart, onMounted, useRef, xml } from "@odoo/owl";
import { loadJS } from "@web/core/assets";

export class PieChartCard extends Component {
  static template = xml`
    <div>
      <p t-esc="props.title"></p>  
      <canvas t-ref="shirtsChart" />
    </div>
  `;

  async setup() {
    this.chart = useRef("shirtsChart");

    onWillStart(async () => {
      this.chart_js = await loadJS("https://cdn.jsdelivr.net/npm/chart.js");
    });

    onMounted(() => {
      new Chart(this.chart.el, {
        type: "pie",
        data: {
          datasets: [
            {
              data: Object.values(this.props.value),
            },
          ],
          labels: Object.keys(this.props.value),
        },
      });
    });
  }
}
