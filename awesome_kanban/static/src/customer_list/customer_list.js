import { Component, onWillStart, useState, reactive } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { fuzzyLookup } from "@web/core/utils/search";
import { usePager } from "@web/search/pager_hook";


export class CustomerList extends Component {
    static template = "awesome_kanban.CustomerList";
    static props = {
        selectCustomer: Function,
    }


    setup() {
        this.orm = useService("orm");
        this.state = useState({ customers: [] });
        this.parameters = reactive({ onlyCompanies: false, searchString: "" }, () => this.refreshCustomers());

        onWillStart(async () => {
            const{ records, length } = await this.loadCustomers();
            this.state.customers = records;
        });
    }

    loadCustomers() {
        const searchDomain = this.parameters.onlyCompanies ? [["is_company", "=", "true"]] : [];
        return this.orm.webSearchRead("res.partner", searchDomain, {
            specification: {
                complete_name: {},
                active: {},
            },
            limit: 15,
        });
    }

    async refreshCustomers() {
        const{ records, length } = await this.loadCustomers();
        if(this.parameters.searchString == "")
            this.state.customers = records;
        else
            this.state.customers = fuzzyLookup(this.parameters.searchString, records, (c) => c.complete_name);
    }
}
