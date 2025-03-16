import { ProductCard } from "@point_of_sale/app/generic_components/product_card/product_card";

ProductCard.props = {
    ...ProductCard.props,
    availableQty: { type: String, optional: true }
};
