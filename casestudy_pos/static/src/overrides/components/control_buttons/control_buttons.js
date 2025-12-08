import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { ClearOrderlineButton } from "./orderline_clear_button/orderline_clear_button";
import { patch } from "@web/core/utils/patch";

patch(ControlButtons, {
    components: {
        ...(ControlButtons.components || {}),
        ClearOrderlineButton
    }
})