import { patch } from "@web/core/utils/patch";
import { ComboConfiguratorPopup } from "@point_of_sale/app/store/combo_configurator_popup/combo_configurator_popup";

patch(ComboConfiguratorPopup.prototype, {
    get_full_product_name(product){
        const full_name = product.display_name;
        const { alternative_name, attribute_line_ids } = product;

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
