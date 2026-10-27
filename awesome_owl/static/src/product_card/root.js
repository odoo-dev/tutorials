import { Component, signal, computed } from "@odoo/owl";
import { ProductCard } from "./product_card"
import { PRODUCTS } from "./products"


export class Root extends Component {
    static components = { ProductCard }
    static template = "tutorial.product_card.root"

    products = PRODUCTS;

    name = signal("");
    mail = signal("");
    greeting = computed(() => `Hello ${this.name()}`);
}