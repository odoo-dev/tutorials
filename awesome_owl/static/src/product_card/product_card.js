import { Component, useProps, t } from "@odoo/owl";

export class ProductCard extends Component {
    static template = "tutorial.product_card"

    props = useProps({
        product : t.object({
            name: t.string(),
            price: t.number(),
            image: t.string().optional("default_image"),
        })
    });
}
