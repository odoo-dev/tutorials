/** @odoo-module **/

import { Component, useState, xml, markup } from "@odoo/owl";
import { Counter } from "./component/counter";
import { Card } from "./component/card";

export class Playground extends Component {
	static template = xml`
    <Card title="'state[0].title'" content="state[0].content" />
    <Card title="state[1].title" content="state[1].content" />
    <Counter />
    <Counter />
    `;
	static components = { Counter, Card };
	static props = { ...this.components.props };

	state = useState([
		{
			title: "why is content stored in state",
			content: content,
		},
		{
			title: "ok nvm i forgot it will try to parse so u have to pass it as string",
			content: content,
		},
	]);
}

const content = markup(`<div class="text-primary">feel222s weird</div>`);
