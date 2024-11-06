import { KanbanController } from "@web/views/kanban/kanban_controller";
import { kanbanView } from "@web/views/kanban/kanban_view";
import { registry } from "@web/core/registry";
import { CustomerList } from "./customer_list/customer_list";


export class AwesomeKanbanController extends KanbanController {
    static template = "awesome_kanban.CustomerKanbanView";
    static components = { ...KanbanController.components, CustomerList };

    setup() {
        super.setup();
    }

    selectCustomer(partner_name, partner_id) {
        const customerFilters = this.env.searchModel.getSearchItems((searchItem) =>
            searchItem.isFromAwesomeKanban
        );

        for (const customerFilter of customerFilters) {
            if (customerFilter.isActive) {
                this.env.searchModel.toggleSearchItem(customerFilter.id);
            }
        }

        this.env.searchModel.createNewFilters([{
            description: partner_name,
            domain: [["partner_id", "=", partner_id]],
            isFromAwesomeKanban: true,
        }])
    }
}
export const awesomeKanbanView = {
    ... kanbanView,
    Controller: AwesomeKanbanController,
}
registry.category("views").add("awesome_kanban", awesomeKanbanView);