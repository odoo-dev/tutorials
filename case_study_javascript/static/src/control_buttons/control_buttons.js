import { patch } from "@web/core/utils/patch";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { usePos } from "@point_of_sale/app/store/pos_hook";

patch(ControlButtons.prototype, {
    setup() {
        super.setup()
        this.pos = usePos();
    },
    removeOrderline() {
        const selectedOrerline = this.currentOrder.get_selected_orderline()
        selectedOrerline.delete()
    }
})