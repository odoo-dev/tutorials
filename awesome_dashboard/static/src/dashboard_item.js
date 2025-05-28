import { Component } from "@odoo/owl";
import { Layout } from "@web/search/layout";


export class DashboardItem extends Component {
    static template = "awesome_dashboard.DashboardItem";
    static components = { Layout };
    static defaultProps = {
        size: 1,
    }
    
    setup() {
        this.size = this.props.size;
        this.widthvalue = (18*this.size);
    }
}
