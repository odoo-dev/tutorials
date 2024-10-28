/** @odoo-module **/

import { Component, xml } from "@odoo/owl";

export default class DashboardItem extends Component {
    static props = {
        size: {type: Number, optional: true},
        text: {type: String},
        content: {type: Object}
    };

    setup() {
        this.test = typeof this.props.content;
    }

    static template = xml`
    <div class="card d-inline-block m-2" style="width: {{18*props.size}}rem;">
        <div class="card-body">
            <t t-out="props.text"/>
            <t t-if="typeof props.content == 'number'">
                <p style="font-size: 2em; color:green;">
                    <t t-out="props.content"/>
                </p>
            </t>
            <t t-if="typeof props.content !== 'number'">
                <div>
                    <t t-out="props.content"/>
                </div>
            </t>
        </div>
    </div>`;
}