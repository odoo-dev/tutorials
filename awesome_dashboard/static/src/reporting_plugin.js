import { Plugin } from "@odoo/owl";
import { services } from "@web/core/services";
import { rpc } from "@web/core/network/rpc";

export class ReportingPlugin extends Plugin{
    loadStatistics() {
        //signature : function rpc(url, params = {}, settings = {})
        return rpc("/awesome_dashboard/statistics", {}, {cache: true});
    }
}

services.add(ReportingPlugin);
