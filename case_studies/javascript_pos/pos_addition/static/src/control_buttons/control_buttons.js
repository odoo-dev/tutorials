import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { patch } from "@web/core/utils/patch";

patch(ControlButtons.prototype, {

    removeOrderline() {

        // For debugging purpose
        // console.log(this)
        // console.log(this.currentOrder)
        // console.log(this.partner)
        // console.log(this.buttonClass)
        // console.log(this.dialog)
        // console.log(this.env)
        // console.log(this.notification)
        // console.log(this.pos)
        // console.log(this.props)
        // console.log(this.ui)

        const currentOrder = this.currentOrder
        const orderLines = currentOrder.get_orderlines()
        const selectedOrderline = currentOrder.get_selected_orderline()

        // For debugging purpose
        // console.log(selectedOrderline)

        if (selectedOrderline) {
            selectedOrderline.delete()

            if (orderLines.length > 0) {
                const lastOrderLine = orderLines[orderLines.length - 1]
                currentOrder.select_orderline(lastOrderLine)
            }
        }
    }

});
