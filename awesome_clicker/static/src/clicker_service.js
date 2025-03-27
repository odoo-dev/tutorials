import { reactive } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { ClickerModel } from "./clicker_model/clicker_model";

export const clickerService = {
  start() {
    const clicker = reactive(new ClickerModel());
    return clicker;
  },
};

registry.category("services").add("clicker", clickerService);
