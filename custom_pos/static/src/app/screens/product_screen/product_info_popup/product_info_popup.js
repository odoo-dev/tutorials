import { patch } from "@web/core/utils/patch";
import { ProductInfoPopup } from "@point_of_sale/app/screens/product_screen/product_info_popup/product_info_popup";
import { ProductCard } from "@point_of_sale/app/generic_components/product_card/product_card";

ProductInfoPopup.props = [
    ...ProductInfoPopup.props,
    "getProductName",
    "getProductPrice",
    "getProductImage",
    "addProductToOrder",
    "state",
    "onProductInfoClick",
    "productsToDisplay",
    "productQuantities"
]

ProductInfoPopup.components = { ...ProductInfoPopup.components, ProductCard };

patch(ProductInfoPopup.prototype, {
    get alternativeProducts() {
        return this.props.productsToDisplay().filter((product)=> this.props.product.raw.pos_alternative_product_ids.includes(product.raw.product_tmpl_id));
    },
});
