/** @odoo-module **/

import { Component, useState, xml, markup } from "@odoo/owl";
import { Counter } from "./component/counter";
import { Card } from "./component/card";

export class Playground extends Component {
	static template = xml`
    <Card title="'data[0].title'" content="data[0].content" />
    <Card title="data[1].title" content="data[1].content" />
    <Counter onChange.bind="incSum"/>
    <Counter onChange.bind="incSum"/>
    <div>Sum is: <t t-esc="this.state.sum"/></div>
    `;
	static components = { Counter, Card };
	static props = { ...this.components.props };

	setup() {
		this.data = [
			{
				title: "why is content stored in state",
				content: content,
			},
			{
				title: "ok nvm i forgot it will try to parse so u have to pass it as string",
				content: content,
			},
		];

		this.state = useState({ sum: 0 });
	}

	incSum() {
		this.state.sum++;
	}
}

const content = markup(`<div class="text-primary">feel222s weird</div>`);
