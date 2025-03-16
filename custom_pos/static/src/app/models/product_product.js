import { patch } from "@web/core/utils/patch";
import { ProductProduct } from '@point_of_sale/app/models/product_product';

patch(ProductProduct.prototype, {
    get searchString() {
        const result = super.searchString;
        return this["alternative_name"] ? `${result} ${this["alternative_name"]}` : result ;
    }
})
