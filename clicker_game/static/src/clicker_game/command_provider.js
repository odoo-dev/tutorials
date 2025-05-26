/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";

const commandProviderRegistry = registry.category("command_provider");

commandProviderRegistry.add("Open Clicker Game", {
    provide: (env, options) => {
        const result = [];
        if (options.searchValue.toLowerCase() === "") {         
            result.push({
                action() {
                    env.services.action.doAction({
                        type: "ir.actions.client",
                        tag: "awesome_clicker.client_action",
                        target: "new",
                        name: "Clicker Game"
                    });
                },
                category: "clicker game",
                name: _t("Open Clicker Game"),
            });
        }
        return result;
    },
});