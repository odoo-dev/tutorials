import { Component, onWillStart, useState } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { Layout } from "@web/search/layout";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";
import { DashboardItem } from "./dashboard_item";
import { ConfigDialog } from "./config_dialog";

class AwesomeDashboard extends Component {
  static template = "awesome_dashboard.AwesomeDashboard";
  static components = { ConfigDialog, DashboardItem, Layout };

  setup() {
    this.display = {
      controlPanel: {},
    };
    this.action = useService("action");

    this.statistics = useState(useService("awesome_dashboard.statistics"));


    this.items = registry.category("awesome_dashboard").getAll();
    this.hiddenItems = useState({value: []})

    onWillStart(async () => {
      this.hiddenItems.value = JSON.parse(await rpc("/awesome_dashboard/get_hidden_items"))
    })

    this.dialogService = useService("dialog");
  }

  openCustomersView() {
    this.action.doAction("base.action_partner_form");
  }

  openLeadsView() {
    this.action.doAction({
      type: "ir.actions.act_window",
      name: "Leads",
      res_model: "crm.lead",
      views: [
        [false, "kanban"],
        [false, "form"],
      ],
    });
  }

  async updateHiddenItems(){
    await rpc("/awesome_dashboard/update_hidden_items", {hidden_items: JSON.stringify(this.hiddenItems.value)})
  }

  openConfigDialog() {
    this.dialogService.add(ConfigDialog, {
      hiddenItems: this.hiddenItems,
      updateHiddenItems: this.updateHiddenItems
    });
  }
}

registry
  .category("actions")
  .add("awesome_dashboard.dashboard", AwesomeDashboard);
