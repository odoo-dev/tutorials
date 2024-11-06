import { Component, onWillStart, useState, reactive } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { fuzzyLookup } from "@web/core/utils/search";


export class CustomerList extends Component {
    static template = "awesome_kanban.CustomerList";
    static props = {
        selectCustomer: Function,
    }

    static parameters = reactive({ onlyCompanies: false, searchString: "" }, () => refreshCustomers());

    setup() {
        this.orm = useService("orm");
        this.state = useState({ customers: [] });

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
            limit: 20,
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
