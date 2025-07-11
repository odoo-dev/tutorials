import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { patch } from "@web/core/utils/patch";

patch(ControlButtons.prototype, {

    removeOrderline() {
        const selectedOrderline = this.currentOrder.get_selected_orderline()

        if (selectedOrderline) {
            selectedOrderline.delete()
        }
    }

});
