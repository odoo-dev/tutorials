/** @odoo-module **/

import {registry} from "@web/core/registry";
import {ClickerModel} from "./clicker_model/clicker_model";


export const clickerService = {
    dependencies: ["effect"],
    start(_env, services) {
        const clickerModel = new ClickerModel();
        const bus = clickerModel.bus;
        bus.addEventListener("MILESTONE_1k", () => {
            services.effect.add({
                type: "rainbow_man", // Default value
                message: "Congratulations! You can now buy a click bot!",
            })
        });
        return clickerModel;
    },
};

registry.category("services").add("clicker_service", clickerService);
