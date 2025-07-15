import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { patch } from "@web/core/utils/patch";

patch(ControlButtons.prototype, {

    removeOrderline() {
        // debugger;

        const currentOrder = this.currentOrder
        const orderLines = currentOrder.get_orderlines()
        const selectedOrderline = currentOrder.get_selected_orderline()

        if (selectedOrderline) {
            selectedOrderline.delete()

            if (orderLines.length > 0) {
                const lastOrderLine = orderLines[orderLines.length - 1]
                currentOrder.select_orderline(lastOrderLine)
            }
        }
    }

});
