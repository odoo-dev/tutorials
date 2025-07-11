import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { patch } from "@web/core/utils/patch";

patch(OrderReceipt.prototype, {
    setup() {
        super.setup()
        this.pos = usePos();

        // For debugging purpose to unpack the pos config
        // console.log(this.pos.config);
    },

    getCongratulatoryText() {
        return this.pos.config.congratulatory_text;
    }

});