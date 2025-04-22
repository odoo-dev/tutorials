/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { loadBundle } from "@web/core/assets";

publicWidget.registry.StudentReport = publicWidget.Widget.extend({
    selector: "#student_report_chart",

    init: function (parent, options) {
        this._super.apply(this, arguments);
    },

    willStart: async function () {
        await loadBundle("web.chartjs_lib");
    },

    start: async function () {
        const ctx = this.el.querySelector('#userChart').getContext('2d');
        const attendance = JSON.parse(this.el.dataset.attendance || "[]")
        const chartData = {
            labels: ['Attended', 'Not Attended', 'Cancelled'],
            datasets: [{
                data: attendance,
                backgroundColor: ['#28a745', '#dc3545', '#ffc107'],
                hoverOffset: 12
            }]
        };

        const chartOptions = {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top'
                },
                title: {
                    display: true,
                    text: 'Class Attendance Overview'
                }
            }
        };

        new Chart(ctx, {
            type: 'doughnut',
            data: chartData,
            options: chartOptions,
            plugins: [{
                id: 'centerText',
                beforeDraw: function (chart) {
                    const ctx = chart.ctx;
                    const { top, bottom, left, right } = chart.chartArea;

                    const centerX = (left + right) / 2;
                    const centerY = (top + bottom) / 2;

                    const [attended, notAttended] = chart.data.datasets[0].data;
                    const total = attended + notAttended;

                    ctx.save();
                    ctx.font = "bold 30px monospace";
                    ctx.textAlign = "center";
                    ctx.textBaseline = "middle";
                    ctx.fillStyle = "#333";
                    ctx.fillText(`Total:${total.toString()}`, centerX, centerY);
                    ctx.restore();
                }
            }]
        });
    }
});
