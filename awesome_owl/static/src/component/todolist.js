import { Component, useState, xml } from "@odoo/owl";
import { TodoItem } from "./todoitem";
import { useAutofocus } from "../utils";

export class TodoList extends Component {
	static template = xml`
    <div class="m-2 p-2 border d-inline-block">
        <h1 class="me-2">Todo List</h1>
		<input t-ref="input" class="form-control" type="text" t-on-keyup="add" placeholder="add new item"/>
		<t t-foreach="state.todo" t-key="item.id" t-as="item">
			<TodoItem todo="item" toggleState.bind="toggleState" removeTodo.bind="removeTodo" />
		</t>
    </div>`;

	static components = { TodoItem };
	static props = {
		...this.components.props,
	};

	setup() {
		useAutofocus("input");
	}

	state = useState({
		todo: [
			{ id: 1, description: "first item", isCompleted: true },
			{ id: 2, description: "second item", isCompleted: false },
		],
	});

	add(e) {
		if (e.keyCode === 13 && e.target.value !== "") {
			this.state.todo.push({
				id: this.state.todo.length + 1,
				description: e.target.value,
				isCompleted: false,
			});
			e.target.value = "";
		}
	}

	toggleState(id) {
		this.state.todo = this.state.todo.map((item) => {
			if (item.id === id) {
				item.isCompleted = !item.isCompleted;
			}
			return item;
		});
	}

	removeTodo(id) {
		this.state.todo = this.state.todo.filter((item) => item.id !== id);
	}
}
