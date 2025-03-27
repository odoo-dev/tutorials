import { Component, xml } from "@odoo/owl";
import { useClicker } from "./clicker_hook";
import { humanNumber } from "@web/core/utils/numbers";

export class ClickValue extends Component {
  static template = xml`
        <span t-out="showValue()" t-att-data-tooltip="this.clicker.clicks" />
    `;

  humanNumber = humanNumber;

  showValue() {
    if (this.clicker.clicks < 1000)
      return humanNumber(this.clicker.clicks);
    else return humanNumber(this.clicker.clicks, { decimals: 1 });
  }
  setup() {
    this.clicker = useClicker();
  }
}
