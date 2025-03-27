import { Component, useExternalListener, markup } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useClicker } from "../clicker_hook";
import { ClickValue } from "../click_value";
import { useService } from "@web/core/utils/hooks";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";

export class Clicker extends Component {
  static template = "awesome_clicker.clicker_systray_item";
  static components = { ClickValue, Dropdown, DropdownItem };

  commandProviderRegistry = registry.category("command_provider");

  setup() {
    this.clicker = useClicker();
    this.effectService = useService("effect");
    console.log(this.clicker.trees);
    useExternalListener(window, "click", () => this.clicker.increment(), {
      capture: true,
    });

    this.clicker.bus.addEventListener("MILESTONE_1k", () =>
      this.displayMilestone("1k", "clickbots")
    );

    this.clicker.bus.addEventListener("MILESTONE_5k", () =>
      this.displayMilestone("5k", "bigbots")
    );

    this.clicker.bus.addEventListener("MILESTONE_100k", () =>
      this.displayMilestone("100k", "power multiplier")
    );

    this.clicker.bus.addEventListener("MILESTONE_1M", () =>
      this.displayMilestone("1M", "and grow trees")
    );

    this.action = useService("action");
    const self = this;

    this.commandProviderRegistry.add("clicker", {
      provide: (env, options) => {
        const result = [];
        result.push({
          action() {
            self.openClicker();
          },
          name: "Open Click Game",
        });

        result.push({
          action() {
            self.clicker.buyClickBot();
          },
          name: "Buy 1 click bot",
        });

        return result;
      },
    });

  }

  openClicker(){
    this.action.doAction({
      type: "ir.actions.client",
      tag: "awesome_clicker.client_action",
      target: "new",
      name: "Clicker Game",
    });
  }

  displayMilestone(milestone, prize) {
    this.effectService.add({
      message: `${milestone} milestone reached! You can now buy {prize}`,
    });
  }
  
}

registry
  .category("systray")
  .add("awesome_clicker.clicker", { Component: Clicker }, { sequence: 52 });
