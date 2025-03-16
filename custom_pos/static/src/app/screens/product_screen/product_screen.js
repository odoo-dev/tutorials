import { patch } from "@web/core/utils/patch";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { reactive } from "@odoo/owl";
import { ProductInfoPopup } from "@point_of_sale/app/screens/product_screen/product_info_popup/product_info_popup";
import { onMounted, onWillStart, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

patch(ProductScreen.prototype, {
    setup() {
        super.setup();
        this.productQuantities = useState({});
        this.quantityService = useService("quantity_service");
        onWillStart(()=> this.fetchProductQty());
        onMounted(()=> this.quantityService.setProductScreenInstance(this));
    },

    getProductName(product) {
        return product.alternative_name || super.getProductName(product);
    },

    async onProductInfoClick(product) {
        const info = await reactive(this.pos).getProductInfo(product, 1);
        this.dialog.add(ProductInfoPopup, {
            info: info,
            product: product,
            getProductName: this.getProductName.bind(this),
            getProductPrice: this.getProductPrice.bind(this),
            getProductImage: this.getProductImage.bind(this),
            addProductToOrder: this.addProductToOrder.bind(this),
            state: this.state,
            onProductInfoClick: this.onProductInfoClick.bind(this),
            productsToDisplay: () => this.productsToDisplay,
            productQuantities: this.productQuantities
        });
    },

    async fetchProductQty() {
            const product_tmpl_ids = this.productsToDisplay.map((product) => product.raw.product_tmpl_id);
            const result = await this.pos.data.read('product.template', product_tmpl_ids, ['qty_available']);
            result.forEach(product => this.productQuantities[product.id] = product.qty_available);
    }
});
