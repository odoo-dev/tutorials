import { Component, useState } from "@odoo/owl"
import { registry } from "@web/core/registry"
import { Layout } from '@web/search/layout'
import { useService } from "@web/core/utils/hooks"
import { DashboardItem } from "./item/item"
import { statisticsService } from './statistics_service'
import { Dialog } from "@web/core/dialog/dialog";
import { CheckBox } from "@web/core/checkbox/checkbox"
import { browser } from "@web/core/browser/browser"


class AwesomeDashboard extends Component {
    static template = "awesome_dashboard.AwesomeDashboard"
    static props = ["*"]
    static components = {Layout, DashboardItem}

    setup() {
        this.action = useService("action")
        this.dialog = useService("dialog")

        this.statistics = useState(
            useService("awesome_dashboard.statistics").data
        )
        this.items = registry.category('awesome_dashboard').getAll()
        this.state = useState({
            disabledItems: browser.localStorage.getItem("disabledDashboardItems")?.split(",") || []
        })
    }

    showCustomers() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Customers',
            target: 'current',
            res_id: 'action_partner_form',
            res_model: 'res.partner',
            views: [[false, 'kanban']],
        })
    }

    showLeads() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Leads',
            target: 'current',
            res_id: 'crm_lead_view_form',
            res_model: 'crm.lead',
            views: [[false, 'list', 'form']],
        })
    }

    openConfiguration() {
        this.dialog.add(ConfigurationDialog, {
            items: this.items,
            disabledItems: this.state.disabledItems,
            onUpdateConfiguration: this.updateConfiguration.bind(this),
        })
    }

    updateConfiguration(newDisabledItems) {
        this.state.disabledItems = newDisabledItems
    }
}

class ConfigurationDialog extends Component {
    static template = "awesome_dashboard.ConfigurationDialog"
    static components = { Dialog, CheckBox }
    static props = ["close", "items", "disabledItems", "onUpdateConfiguration"]

    setup() {
        this.items = useState(this.props.items.map((item) => {
            return {
                ...item,
                enabled: !this.props.disabledItems.includes(item.id),
            }
        }))
    }

    done() {
        this.props.close()
    }

    onChange(checked, changedItem) {
        changedItem.enabled = checked
        const newDisabledItems = Object.values(this.items).filter(
            (item) => !item.enabled
        ).map(item => item.id)

        browser.localStorage.setItem(
            "disabledDashboardItems",
            newDisabledItems,
        )
        this.props.onUpdateConfiguration(newDisabledItems)
    }

}

registry.category("lazy_components").add("AwesomeDashboard", AwesomeDashboard)
registry.category("services").add("awesome_dashboard.statistics", statisticsService)
