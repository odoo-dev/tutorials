import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";

patch(PosOrder.prototype, {
    setSalesPerson(sales_person) {
        this.salesperson_id = sales_person;
    },
    getSalesPerson() {
        return this.models["res.users"].get(this.salesperson_id.id);
    }
})
