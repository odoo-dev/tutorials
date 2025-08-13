import { Component, useState, xml } from "@odoo/owl";

export class Card extends Component {
	static template = xml`
    <div class="card d-inline-block m-2" style="width: 18rem;">
        <div class="card-body">
            <h5 class="card-title">
                <t t-slot="title"/>
                <button class="btn btn-primary" type="button" t-on-click="toggleShowContent">
                toggle
                </button>
            </h5>
            <p class="card-text" t-att-hidden="this.state.showContent">
                <t t-slot="content" />
                <t t-slot="default" />
            </p>
        </div>
    </div>
    `;

	static props = {
		slots: {
			type: Object,
			shape: {
				title: { type: true, optional: true },
				content: { type: true, optional: true },
				default: { type: true, optional: true },
			},
		},
	};

	state = useState({
		showContent: false,
	});

	toggleShowContent() {
		this.state.showContent = !this.state.showContent;
	}
}
