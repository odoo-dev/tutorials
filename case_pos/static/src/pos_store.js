import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";

patch(PosStore.prototype, {
    getReceiptHeaderData(order) {
        let data = super.getReceiptHeaderData(order);
        data.congratulatory_text = this.config.congratulatory_text
        return data;
    }
});
