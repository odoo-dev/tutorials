import { _t } from "@web/core/l10n/translation";
import { Component } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import { CheckBox } from "@web/core/checkbox/checkbox";
import { registry } from "@web/core/registry";

export class ConfigDialog extends Component {
  static template = "awesome_dashboard.ConfigDialog";
  static components = { Dialog, CheckBox };
  static props = {
    close: Function,
    hiddenItems: Array,
  };

  setup() {
    this.items = registry.category("awesome_dashboard").getAll();
  }

  onChange(event) {
    if (!event.target.checked) {
      this.props.hiddenItems.push(event.target.id);
    } else {
      const itemIndex = this.props.hiddenItems.findIndex(
        (item) => item === event.target.id
      );
      if (itemIndex !== -1) {
        this.props.hiddenItems.splice(itemIndex, 1);
      }
    }
  }

  onClose() {
    this.props.close();
  }
}
