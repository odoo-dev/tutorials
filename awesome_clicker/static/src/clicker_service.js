/** @odoo-module **/

import {registry} from "@web/core/registry";
import {ClickerModel} from "./clicker_model/clicker_model";


export const clickerService = {
    start(_env) {
        return new ClickerModel();
    },
};

registry.category("services").add("clicker_service", clickerService);
