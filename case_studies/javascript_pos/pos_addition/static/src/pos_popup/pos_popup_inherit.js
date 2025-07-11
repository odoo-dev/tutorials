import { ProductInfoPopup } from "@point_of_sale/app/screens/product_screen/product_info_popup/product_info_popup";
import { patch } from "@web/core/utils/patch";

patch(ProductInfoPopup.prototype, {
    setup() {
        super.setup()
        
        // For debugging purpose: to unpack the props
        // console.log(this.props);
    },
});