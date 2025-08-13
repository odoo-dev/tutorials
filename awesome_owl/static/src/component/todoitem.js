import { Component, xml } from "@odoo/owl";

export class TodoItem extends Component {
	static template = xml`
    <div class="d-flex gap-2"> 
        <input type="checkbox" t-att-id="props.todo.id" t-att-checked="props.todo.isCompleted" t-on-change="onChange" />  
        <span t-att-class="props.todo.isCompleted ? 'text-decoration-line-through text-muted' : ''">
            <t t-esc="props.todo.id"/>. <t t-esc="props.todo.description"/>
        </span>
        <span class="fa fa-remove text-danger" t-on-click="onRemove" />
    </div>`;

	static props = {
		todo: {
			type: Object,
			shape: {
				id: { type: Number },
				description: { type: String },
				isCompleted: { type: Boolean },
			},
		},
		toggleState: Function,
		removeTodo: Function,
	};

	onChange() {
		this.props.toggleState(this.props.todo.id);
	}

    onRemove() {
        this.props.removeTodo(this.props.todo.id);
    }
}
