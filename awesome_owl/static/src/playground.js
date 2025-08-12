/** @odoo-module **/

import { Component, useState, xml } from "@odoo/owl";
import { Counter } from "./component/counter";
import { Card } from "./component/card";

export class Playground extends Component {
	static template = xml`
    <Card title="state[0].title" content="state[0].content" />
    <Card title="state[1].title" content="state[1].content" />
    <Counter />
    <Counter />
    `;
	static components = { Counter, Card };

	state = useState([
		{
			title: "why is content stored in state",
			content: "feels weird",
		},
		{
			title: "why is content st22ored in state",
			content: "feel222s weird",
		},
	]);
}
