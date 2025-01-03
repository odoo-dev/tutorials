/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component, useState, xml } from "@odoo/owl";

export class TodoApp extends Component {
    static template = xml`
        <div class="todo-app">
            <h1>OWL To-Do App</h1>
            <div class="task-input">
                <input t-model="state.newTask" placeholder="Add a new task..." />
                <button t-on-click="addTask">Add</button>
            </div>
            <ul>
                <t t-foreach="state.tasks" t-as="task" t-key="task.id">
                    <li>
                        <input type="checkbox" t-att-checked="task.is_done" t-on-change="() => toggleTask(task)" />
                        <span t-att-class="task.is_done ? 'done' : ''"><t t-esc="task.name" /></span>
                        <button t-on-click="(this) => deleteTask(task)">Delete</button>
                    </li>
                </t>
            </ul>
        </div>
    `;
    setup() {
        this.state = useState({
            tasks: this.loadTasks(),
            newTask: "",
        });
    }

    loadTasks() {
        // Load tasks from localStorage or initialize with an empty array
        const storedTasks = localStorage.getItem("owl_todo_tasks");
        return storedTasks ? JSON.parse(storedTasks) : [];
    }

    saveTasks() {
        // Save tasks to localStorage
        localStorage.setItem("owl_todo_tasks", JSON.stringify(this.state.tasks));
    }

    addTask() {
        if (!this.state.newTask.trim()) return;

        this.state.tasks.push({
            id: Date.now(), // Use timestamp as a unique ID
            name: this.state.newTask,
            is_done: false,
        });

        this.state.newTask = "";
        this.saveTasks();
    }

    toggleTask(task) {
        task.is_done = !task.is_done;
        this.saveTasks();
    }

    deleteTask(task) {
        this.state.tasks = this.state.tasks.filter((t) => t.id !== task.id);
        this.saveTasks();
    }
}

registry.category("actions").add("owl_example.dashboard", TodoApp);
