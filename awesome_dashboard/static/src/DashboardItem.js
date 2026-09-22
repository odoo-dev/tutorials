import {Component, useState, xml} from "@odoo/owl";

export class DashboardItem extends Component {
    static template = xml`
        <div class="card d-inline-block m-2  flex-grow-1" t-attf-style="width: {{18* this.props.size}}rem">
        <div class="card-body">
        <h5 class="card-title"><t t-slot="title" /></h5>
           <p class="card-text">
            <t t-slot="default"/>
            <div style="text-align: center;">
                    <t t-esc="props.value" />            
            </div>
            </p>
        </div>
        </div>    `
    static props = {
        size: {type: Number, optional: true},
        value: {type: Number, optional: true},
        slots: {optional: true},
    }
    static defaultProps = {
        size: 1,
    };

}