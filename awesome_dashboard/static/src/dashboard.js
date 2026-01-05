import { Component, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";
import { Layout } from "@web/search/layout";
import { DashboardItem } from "./dashboard-item/dashboard-item";
import { useService } from "@web/core/utils/hooks";

class AwesomeDashboard extends Component {
  static template = "awesome_dashboard.AwesomeDashboard";
  static components = { Layout, DashboardItem };

  setup() {
    debugger;
    this.action = useService("action");
    this.data = {};
    this.error = null;
    this.loading = false;
    onWillStart(async () => {
      this.loading = true;
      try {
        const result = await rpc("/awesome_dashboard/statistics");
        this.data = result;
        this.error = null;
      } catch (error) {
        this.error = error;
        this.data = {};
      } finally {
        this.loading = false;
      }
    });
  }

  openSettings() {
    this.action.doAction("base_setup.action_general_configuration");
  }

  openLeads() {
    this.action.doAction({
      type: "ir.actions.act_window",
      name: "All leads",
      res_model: "crm.lead",
      views: [
        [false, "list"],
        [false, "form"],
      ],
    });
  }

  openCustomers() {
    this.action.doAction("base.action_partner_form");
  }
}

registry
  .category("actions")
  .add("awesome_dashboard.dashboard", AwesomeDashboard);
