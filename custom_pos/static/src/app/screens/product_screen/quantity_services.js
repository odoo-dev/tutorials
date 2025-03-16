import { registry } from "@web/core/registry";

export const QuantityService = {
    async start() {
        let ProductScreenInstance = {};
        return {
            setProductScreenInstance(instance) {
                ProductScreenInstance = instance;
            },

            async fetchProductQty() {
                if(!ProductScreenInstance) {
                    console.warn("Product Screen is not set");
                    return;
                }
                await ProductScreenInstance.fetchProductQty();
            }
        };
    },
};

registry.category("services").add("quantity_service", QuantityService);
