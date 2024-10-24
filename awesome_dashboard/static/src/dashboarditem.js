/** @odoo-module **/

import { Component, xml } from "@odoo/owl";

export default class DashboardItem extends Component {
    static props = {
        size: {type: Number, optional: true},
        text: {type: String},
        content: {type: String}
    };

    static template = xml`
    <div class="card d-inline-block m-2" style="width: 18rem;">
        <div class="card-body">
            <t t-out="props.text"/>
            <p style="font-size: 2em; color:green;">
                <t t-out="props.content"/>
            </p>
        </div>
    </div>`;
}