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
        this.resModel = this.props.context.product_catalog_order_model;
        this.startBarcodeScanner();
    },

    startBarcodeScanner() {
        this.barcode.bus.addEventListener("barcode_scanned", this.onBarcodeScanned.bind(this));
    },

    async onBarcodeScanned(event) {
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
            if (this.resModel === "sale.order") {
                orderLineModel = "sale.order.line";
                quantityField = "product_uom_qty";
            } else if (this.resModel === "purchase.order") {
                orderLineModel = "purchase.order.line";
                quantityField = "product_qty";
            } else {
                console.error("Unsupported order model:", this.resModel);
                return;
            }

            const orderLines = await this.orm.searchRead(
                orderLineModel,
                [["order_id", "=", this.orderId], ["product_id", "=", product.id]],
                ["id", quantityField]
            );

            let newQuantity = 1;

            if (orderLines.length > 0) {
                const orderLine = orderLines[0];
                newQuantity = orderLine[quantityField] + 1;

                await this.orm.write(orderLineModel, [orderLine.id], {
                    [quantityField]: newQuantity,
                });
            } else {
                await rpc("/product/catalog/update_order_line_info", {
                    res_model: this.resModel,
                    order_id: this.orderId,
                    product_id: product.id,
                    quantity: newQuantity,
                });
            }

            this.notification.add(
                `Added ${product.name} to order (Quantity: ${newQuantity})`,
                { type: "success" }
            );

            this.model.load();
        } catch (error) {
            console.error("Error processing barcode scan:", error);
        }
    },

});
