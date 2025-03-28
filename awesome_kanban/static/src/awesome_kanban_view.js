/** @odoo-module */

// TODO: Define here your AwesomeKanban view
import { kanbanView } from "@web/views/kanban/kanban_view";
import { registry } from "@web/core/registry";
import { KanbanListController } from "./kanban_list_controller";

export const KanbanListView = {
    ...kanbanView,
    Controller: KanbanListController,
};

registry.category("views").add("awesome_kanban", KanbanListView);