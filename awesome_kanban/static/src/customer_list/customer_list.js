import { Component, xml, onWillStart, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { fuzzyLookup } from "@web/core/utils/search";
import { Pager } from "@web/core/pager/pager";

export class CustomerList extends Component {
  static template = "awesome_kanban.customer_list";
  static components = { Pager };
  static props = {
    selectCustomer: {
      type: Function,
    },
  };

  setup() {
    this.orm = useService("orm");
    this.state = useState({
      activePartners: false,
      searchInput: "",
      prevDisplayedCustomers: [],
      pager: {
        offset: 0,
        limit: 20,
      },
    });

    onWillStart(async () => {
      this.partners = await this._fetchCustomers();
      this.activePartners = this._filterCustomers(this.partners);
    });
  }

  updatePager({ offset }) {
    this.state.pager.offset = offset;
  }

  get Customers() {
    return this.lookUp(
      this.state.searchInput,
      this.state.activePartners ? this.activePartners : this.partners
    );
  }

  get displayedCustomers() {
    return this.Customers.slice(
      this.state.pager.offset,
      this.state.pager.offset + this.state.pager.limit
    );
  }

  lookUp(pattern, partners) {
    if (pattern == "") return partners;
    else {
      return fuzzyLookup(pattern, partners, (partner) => partner.display_name);
    }
  }

  _filterCustomers(customers) {
    return customers.filter((customer) => customer.opportunity_ids.length >= 1);
  }

  async _fetchCustomers() {
    const data = await this.orm.searchRead(
      "res.partner",
      [],
      ["display_name", "opportunity_ids"]
    );
    return data;
  }
}
