import { Component, xml } from "@odoo/owl";

export class NumberCard extends Component {
  static template = xml`
        <div class="card text-center">
            <p t-esc="props.title"></p>
            <p class="fs-1 fw-bold text-success">
                <t t-esc="props.value" />
            </p>
        </div>
    `;
  
}
