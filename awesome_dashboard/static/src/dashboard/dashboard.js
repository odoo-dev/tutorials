/** @odoo-module **/

import {Component, useState} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {Layout} from "@web/search/layout";
import {useService} from "@web/core/utils/hooks";
import {_t} from "@web/core/l10n/translation";
import {DashboardItem} from "./dashboard_item/dashboard_item";
import {PieChart} from "./pie_chart/pie_chart";
import {CheckBox} from "@web/core/checkbox/checkbox";
import {Dialog} from "@web/core/dialog/dialog";
import {browser} from "@web/core/browser/browser";

class AwesomeDashboard extends Component {
    static template = "awesome_dashboard.AwesomeDashboard";
    static components = {Layout, DashboardItem, PieChart};

    setup() {
        this.action = useService("action");
        this.dialog = useService("dialog");
        this.statistics = useState(useService("awesome_dashboard.statistics"));
        this.items = registry.category("awesome_dashboard").getAll();
        this.state = useState({
            selectedItems: browser.localStorage.getItem("selectedItems")?.split(",") || []
        });
    }

    openCustomersKanban() {
        this.action.doAction("base.action_partner_form");
    }

    async openLeads(activity) {
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: _t('Leads'),
            target: 'current',
            res_id: activity.res_id,
            res_model: 'crm.lead',
            views: [[false, 'list'], [false, 'form']],
        });
    }

    openConfigurationDialog() {
        this.dialog.add(ConfigurationDialog, {
            items: this.items,
            selectedItems: this.state.selectedItems,
            onClose: () => this.dialog.close(),
            onChange: this.onChangeSelectedItems.bind(this),
        });
    }

    onChangeSelectedItems(newSelectedItems) {
        this.state.selectedItems = newSelectedItems;
    }
}

class ConfigurationDialog extends Component {
    static template = "awesome_dashboard.ConfigurationDialog";
    static components = {Dialog, CheckBox};
    static props = {
        items: {type: Array, optional: true},
        selectedItems: {type: Array, optional: true},
        onClose: {type: Function, optional: true},
        onChange: {type: Function, optional: true},
    };

    setup() {
        this.items = useState(this.props.items.map((item) => {
            return {
                ...item, enabled: this.props.selectedItems.includes(item.id),
            }
        }));
    }

    done() {
        this.props.close();
    }

    onChange(checked, changedItem) {
        changedItem.enabled = checked;
        const newSelectedItems = Object.values(this.items).filter(
            (item) => item.enabled
        ).map((item) => item.id)

        browser.localStorage.setItem(
            "selectedItems",
            newSelectedItems,
        );

        this.props.onChange(newSelectedItems);
    }
}

registry.category("lazy_components").add("AwesomeDashboard", AwesomeDashboard);