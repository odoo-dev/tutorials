/** @odoo-module **/

import { Component, useState, xml } from "@odoo/owl";
import { Counter } from "./component/counter";
import { Card } from "./component/card";

export class Playground extends Component {
	static template = xml`
    <div class="p-3">
        hello world
    </div>
    <Card title="state.title" content="state.content" />
    <Counter />
    <Counter />
    `;
	static components = { Counter, Card };

	state = useState({
		title: "why is content stored in state",
		content: "feels weird",
	});
}
