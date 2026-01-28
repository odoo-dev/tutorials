import { browser } from "@web/core/browser/browser";
import { registry } from "@web/core/registry";
import { onMounted, onWillUnmount } from "@odoo/owl";
import { kanbanView } from "@web/views/kanban/kanban_view";


class ShelterKanbanController extends kanbanView.Controller {
    setup() {
        super.setup();
        let interval;
    
        onMounted(() => (interval = browser.setInterval(() => this.model.load(), 10 * 1000)));
        onWillUnmount(() => browser.clearInterval(interval));
    }
}

registry.category("views").add("shelter_kanban", { ...kanbanView, Controller: ShelterKanbanController });
