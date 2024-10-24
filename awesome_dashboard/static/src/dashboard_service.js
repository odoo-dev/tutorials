/** @odoo-module **/

import { registry } from "@web/core/registry";
import { onWillStart } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";


export const dashboardService = {
    start() {
        onWillStart(async () => {
        this.result = await rpc("/awesome_dashboard/statistics");

        });

        return {
            getData() {
                return this.result;
            }
        }
    }
};

registry.category("services").add("awesome_dashboard.statistics", dashboardService);
