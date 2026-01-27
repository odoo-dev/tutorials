import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";


class LongStayBanner extends Component {
    static template = "awesome_shelter.LongStayBanner";
}

registry.category("view_widgets").add("long_stay_banner", LongStayBanner);
