import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardWidgetProps } from "@web/views/widgets/standard_widget_props";


class LongStayBanner extends Component {
    static template = "awesome_shelter.LongStayBanner";
    static props = { ...standardWidgetProps };
}

registry.category("view_widgets").add("long_stay_banner", { component: LongStayBanner });
