import { Component, xml } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { ClickValue } from "../click_value";
import { useClicker } from "../clicker_hook";
import { Notebook } from "@web/core/notebook/notebook";

export class ClientAction extends Component {
  static template = "awesome_clicker.client_action";
  static components = { ClickValue, Notebook };

  setup() {
    this.clicker = useClicker();
  }
}

export class OpenClient extends Component {
  static template = xml`
        <button style="align-self: center" class="btn btn-secondary" t-on-click="open">Open</button>
    `;

  setup() {
    this.action = useService("action");
  }

  open() {
    this.action.doAction({
      type: "ir.actions.client",
      tag: "awesome_clicker.client_action",
      target: "new",
      name: "Clicker Game",
    });
  }
}

registry.category("actions").add("awesome_clicker.client_action", ClientAction);
