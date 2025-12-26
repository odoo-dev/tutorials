import {Component, useState, useRef, onMounted} from "@odoo/owl";
import {TodoItem} from "../item/todo_item";
import {useAutoFocus} from "../../utils/utils";

export class TodoList extends Component {
    static template = "awesome_owl.todo_list";

    static components = {TodoItem};

    static props = {
        items: {
            type: Array,
            optional: true,
        }
    }

    setup() {
        this.props.items = useState([])
        this.descriptionRef = useRef('descriptionInput');
        this.nextId = 1;
        onMounted(() => {
            useAutoFocus(this.descriptionRef.el)
        });
    }

    #checkDescription() {
        return this.descriptionRef?.el?.value?.trim();
    }

    addTodoItem() {
        if (this.#checkDescription()) {
            this.props.items.push({
                id: this.nextId++,
                description: this.descriptionRef.el.value,
                isCompleted: false
            })
            this.descriptionRef.el.value = '';
        }
    }

    checkAndAddTask(ev) {
        if (ev.keyCode === 13 && this.#checkDescription()) {
            this.addTodoItem();
        }
    }

    toggleTodoState = (id, isChecked) => {
        const element = this.props.items.find(item => item.id === id);
        if (element) {
            element.isCompleted = isChecked;
        }
    }

    removeTodoItem = (id) => {
        const index = this.props.items.findIndex(item => item.id === id);
        if(index >= 0) {
            this.props.items.splice(index, 1);
        }
    }
}
