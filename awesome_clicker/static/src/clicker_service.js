/** @odoo-module */

import { registry } from "@web/core/registry";
import { ClickerModel } from "./clicker_model";

const ClickerService = {
    dependencies: ["effect"],
    start(env, services) { 
        const clickerModel = new ClickerModel();

        const bus = clickerModel.bus;

        bus.addEventListener("MILESTONE", (ev) => {
            services.effect.add({
                message: `Milestone reached! You can now buy ${ev.detail.unlock}`,
            })
        })

        return clickerModel;
    },
};

registry.category("services").add("awesome_clicker.clicker", ClickerService);
