/** @odoo-module **/

import { Component, markup, onMounted, onWillStart, onWillUnmount, useEffect, useRef, useState, xml } from "@odoo/owl";
import { loadJS } from "@web/core/assets";
import { browser } from "@web/core/browser/browser";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Layout } from "@web/search/layout";
import { DashboardItem } from "./dashboard_item/dashboard_item";
import { DashboardDialog } from "./dialog/dashboard_dialog";

class AwesomeDashboard extends Component {
    static template = "awesome_dashboard.AwesomeDashboard";
    static components = { DashboardItem, Layout }

    setup() {
        this.display = {
            controlPanel: { },
        };
        this.action = useService("action");
        this.dialog = useService("dialog");

        this.statistics = useService("awesome_dashboard.statistic");
        this.result = useState(this.statistics.state.data);

        this.items = registry.category("awesome_dashboard").getAll();

        this.storageKey = ["awesome_dashboard_item"];
        this.setupActiveDashboardItem();
    }

    openCustomers() {
        this.action.doAction("base.action_partner_form");
    }

    openLeads() {
        console.log("Opening Leads");
        this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'crm.lead',
            views: [[false, 'list'], [false,'form']],
        });
    }

    openDialog() {
        this.dialog.add(DashboardDialog, {
            items: this.items,
            activeDashboardItem: this.activeDashboardItem,
            storageKey: this.storageKey,
        });
    }

    get activeItems() {
        return this.items.filter(
            (item) => this.activeDashboardItem[item.id]
        );
    }

    setupActiveDashboardItem() {
        const activeDashboardItemList = browser.localStorage.getItem(this.storageKey)?.split(",");

        this.activeDashboardItem = useState({});
        for (const item of this.items) {
            if (activeDashboardItemList) {
                this.activeDashboardItem[item.id] = activeDashboardItemList.includes(
                    item.id.toString()
                );
            } else {
                this.activeDashboardItem[item.id] = true;
            }
        }
    }
}

// registry.category("actions").add("awesome_dashboard.dashboard", AwesomeDashboard);
registry.category("lazy_components").add("AwesomeDashboard", AwesomeDashboard);
