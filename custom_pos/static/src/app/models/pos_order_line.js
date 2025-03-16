import { patch } from "@web/core/utils/patch";
import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";

patch(PosOrderline.prototype, {
    get_full_product_name() {
        const full_name = super.get_full_product_name();
        const { alternative_name, attribute_line_ids } = this.product_id;

        if(!alternative_name) {
            return full_name;
        }
        if(attribute_line_ids.length > 0) {
            const attribute_index = full_name.lastIndexOf('(');
            const attribute_name = attribute_index !== -1 ? full_name.slice(attribute_index) :  '';
            return `${alternative_name} ${attribute_name}`;
        }
        return alternative_name;
    }
});
