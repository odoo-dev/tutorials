import { Component, useState, xml } from "@odoo/owl";

export class Counter extends Component {
	static template = xml`
	<div class="m-2 p-2 border d-inline-block">
		<span class="me-2">Counter: <t t-esc="state.value"/></span>
		<button class="btn btn-primary" t-on-click="increment">Increment</button>
	</div>`;
	static props = {
		onChange: Function,
	};

	setup() {
		this.state = useState({ value: 0 });
	}

	increment() {
		this.state.value++;
		if (this.props.onChange) {
			this.props.onChange();
		}
	}
}
