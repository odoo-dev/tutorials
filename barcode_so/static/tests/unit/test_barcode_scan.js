/** @odoo-module **/

import { createWebClient, doAction } from "@web/../tests/webclient/helpers";
import { registry } from "@web/core/registry";
import { getFixture } from "@web/../tests/helpers/utils";
import { barcodeService } from "@web/core/barcode/barcode_service";
import { rpc } from "@web/core/network/rpc";

QUnit.module("POS Barcode Scanning", {
    beforeEach: function () {
        var self = this;
        registry.category("services").add("barcode", barcodeService, { force: true });

        this.clientData = {
            action: {
                tag: "product_catalog_kanban",
                type: "ir.actions.client",
                res_model: "product.product",
                context: { order_id: 1 },
            },
            products: [
                { id: 1, name: "Test Product A", barcode: "123456", qty: 1 },
                { id: 2, name: "Test Product B", barcode: "654321", qty: 2 },
            ],
            orderLines: [{ id: 10, product_id: 1, quantity: 1 }], // Product A is already in the order
        };

        this.mockRPC = function (route, args) {
            if (route === "/product/catalog/order_lines_info") {
                return Promise.resolve(self.clientData.orderLines);
            }
            if (route === "/product/catalog/update_order_line_info") {
                return Promise.resolve({ success: true });
            }
            if (route.includes("product.product")) {
                const foundProduct = self.clientData.products.find(p => p.barcode === args.domain[0][2]);
                return Promise.resolve(foundProduct ? [foundProduct] : []);
            }
        };
    },
});

QUnit.test("Scan barcode - Add new product", async function (assert) {
    assert.expect(2);

    const target = getFixture();
    const webClient = await createWebClient({ mockRPC: this.mockRPC });
    await doAction(webClient, this.clientData.action);

    // Simulate barcode scanning (new product)
    webClient.services.barcode.bus.trigger("barcode_scanned", { detail: { barcode: "654321" } });

    await new Promise(resolve => setTimeout(resolve, 500)); // Wait for UI update

    assert.containsOnce(target, ".product[data-id='2']", "New product should be added to the order");
    assert.containsOnce(target, ".o_notification", "Success notification should appear");
});

QUnit.test("Scan barcode - Increase quantity of existing product", async function (assert) {
    assert.expect(2);

    const target = getFixture();
    const webClient = await createWebClient({ mockRPC: this.mockRPC });
    await doAction(webClient, this.clientData.action);

    // Simulate barcode scanning (existing product)
    webClient.services.barcode.bus.trigger("barcode_scanned", { detail: { barcode: "123456" } });

    await new Promise(resolve => setTimeout(resolve, 500));

    assert.strictEqual(
        this.clientData.orderLines.find(line => line.product_id === 1).quantity,
        2,
        "Existing product quantity should increase"
    );
    assert.containsOnce(target, ".o_notification", "Success notification should appear");
});

QUnit.test("Scan barcode - Invalid barcode", async function (assert) {
    assert.expect(1);

    const target = getFixture();
    const webClient = await createWebClient({ mockRPC: this.mockRPC });
    await doAction(webClient, this.clientData.action);

    // Simulate barcode scanning (invalid product)
    webClient.services.barcode.bus.trigger("barcode_scanned", { detail: { barcode: "999999" } });

    await new Promise(resolve => setTimeout(resolve, 500));

    assert.containsOnce(target, ".o_notification", "Error notification should appear for unknown barcode");
});
