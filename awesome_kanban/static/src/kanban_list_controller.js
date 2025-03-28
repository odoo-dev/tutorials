import { KanbanController } from "@web/views/kanban/kanban_controller";
import { CustomerList } from "./customer_list/customer_list";

export class KanbanListController extends KanbanController {
  static template = "awesome_kanban.kanban_list";
  static components = { ...KanbanController.components, CustomerList };

  setup() {
    super.setup();
  }

  selectCustomer(partner_id, partner_name) {
    const customerFilters = this.env.searchModel.getSearchItems(
      (searchItem) => searchItem.isFromAwesomeKanban
    );

    for (const customerFilter of customerFilters) {
      if (customerFilter.isActive) {
        this.env.searchModel.toggleSearchItem(customerFilter.id);
      }
    }

    this.env.searchModel.createNewFilters([
      {
        description: partner_name,
        domain: [["partner_id", "=", partner_id]],
        isFromAwesomeKanban: true, 
      },
    ]);
  }
}
