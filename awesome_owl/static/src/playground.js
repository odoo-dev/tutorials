/** @odoo-module **/

import { Component, useState, xml, markup, htmlEscape } from "@odoo/owl";
import { Counter } from "./component/counter";
import { Card } from "./component/card";
import { TodoList } from "./component/todolist";

export class Playground extends Component {
	static template = xml`
    <div class="d-flex flex-wrap">
        <t t-foreach="this.data" t-as="item" t-key="item.title">
            <Card>
                <t t-set-slot="title">
                    <t t-esc="item.title"/>
                </t>
                <t t-set-slot="content">
                    <t t-out="item.content"/>
                </t>
				<Counter onChange.bind="incSum"/>
            </Card>
        </t>
    </div>
    <div>Sum is: <t t-esc="this.state.sum"/></div>

	<TodoList />
    `;
	static components = { Counter, Card, TodoList };
	static props = { ...this.components.props };

	data = [
		{
			title: "why is content stored in state",
			content: htmlEscape(content),
		},
		{
			title: "ok nvm i forgot it will try to parse so u have to pass it as string",
			content: content,
		},
	];

	state = useState({ sum: 0 });

	incSum() {
		this.state.sum++;
	}
}

const content = markup(`<div class="text-primary">some formatted stuff</div>`);
