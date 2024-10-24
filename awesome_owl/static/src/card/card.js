/** @odoo-module **/

import { Component, xml } from "@odoo/owl";

export default class Card extends Component {
    static props = ["title", "text"];

    static template = xml`
        <div class="card d-inline-block m-2" style="width: 18rem;">
            <div class="card-body">
                <h5 class="card-title">
                    <t t-out="props.title"/>
                </h5>
                <p class="card-text">
                    <t t-out="props.text"/>
                </p>
            </div>
        </div>`;
}
