import { whenReady } from "@odoo/owl";
import { mountComponent } from "@web/env";
import { TodoApp } from "../components/task";

whenReady(() => mountComponent(TodoApp, document.body));
