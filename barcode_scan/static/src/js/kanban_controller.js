import { patch } from "@web/core/utils/patch";
import { ProductCatalogKanbanController } from "@product/product_catalog/kanban_controller";
import { rpc } from "@web/core/network/rpc";
import { useService } from "@web/core/utils/hooks";

patch(ProductCatalogKanbanController.prototype, {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.barcode = useService("barcode");
        this.notification = useService("notification");
        this.orderId = this.props.context.order_id;
        this.orderResModel = this.props.context.product_catalog_order_model;
        this.startBarcodeScanner();
    },

    startBarcodeScanner() {
        this.barcode.bus.addEventListener("barcode_scanned", async (event) => {
            const scannedBarcode = event.detail.barcode;

            try {
                const products = await this.orm.searchRead(
                    "product.product",
                    [["barcode", "=", scannedBarcode]],
                    ["id", "name"]
                );

                if (!products.length) {
                    this.notification.add("No product found", { type: "warning" });
                    return;
                }

                const product = products[0];

                let orderLineModel, quantityField;
                if (this.orderResModel === "sale.order") {
                    orderLineModel = "sale.order.line";
                    quantityField = "product_uom_qty";
                } else if (this.orderResModel === "purchase.order") {
                    orderLineModel = "purchase.order.line";
                    quantityField = "product_qty";
                } else {
                    console.error("Unsupported order model:", this.orderResModel);
                    return;
                }

                const existingOrderLines = await this.orm.searchRead(
                    orderLineModel,
                    [["order_id", "=", this.orderId], ["product_id", "=", product.id]],
                    ["id", quantityField],
                );

                const updatedQuantity = existingOrderLines.length ? existingOrderLines[0][quantityField] + 1 : 1;

                await rpc("/product/catalog/update_order_line_info", {
                    res_model: this.orderResModel,
                    order_id: this.orderId,
                    product_id: product.id,
                    quantity: updatedQuantity,
                });

                this.notification.add(
                    `Added ${product.name} to order (Quantity: ${updatedQuantity})`,
                    { type: "success" }
                );

                this.model.load();

            } catch (error) {
                console.error("Error processing barcode scan:", error);
            }
        });
    },
});
