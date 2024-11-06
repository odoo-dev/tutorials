import { Component, onWillStart, useState, reactive } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { fuzzyLookup } from "@web/core/utils/search";
import { Pager } from "@web/core/pager/pager";


export class CustomerList extends Component {
    static template = "awesome_kanban.CustomerList";
    static props = {
        selectCustomer: Function,
    }

    static components = { Pager };

    setup() {
        this.orm = useService("orm");
        this.state = useState({ customers: [] });
        this.parameters = reactive({ onlyCompanies: false, searchString: "" }, () => this.refreshCustomers());
        this.pagerParams = useState({ offset: 0, limit: 10 });

        onWillStart(async () => {
            this.refreshCustomers();
        });
    }

    loadCustomers() {
        const searchDomain = this.parameters.onlyCompanies ? [["is_company", "=", "true"]] : [];
        return this.orm.webSearchRead("res.partner", searchDomain, {
            specification: {
                complete_name: {},
                active: {},
            },
            limit: this.pagerParams.limit,
            offset: this.pagerParams.offset,
        });
    }

    async refreshCustomers() {
        const{ records, length } = await this.loadCustomers();
        if(this.parameters.searchString == "") {
            this.state.customers = records;
            this.pagerParams.total = length;
        }
        else {
            this.state.customers = fuzzyLookup(this.parameters.searchString, records, (c) => c.complete_name);
            this.pagerParams.total = this.state.customers.length;
        }
    }

    async updatePager(newState) {
        Object.assign(this.pagerParams, newState);
        this.refreshCustomers();
    }
}
