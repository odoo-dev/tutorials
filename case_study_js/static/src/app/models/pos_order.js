import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";

patch(PosOrder.prototype, {
    export_for_printing(baseUrl, headerData) {
        const res = super.export_for_printing(...arguments);
        res.congratulatory_message = this.config.congratulatory_message;
        return res;
    }
});
