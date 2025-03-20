import { expect, test } from "@odoo/hoot";
import { defineModels, models, fields, mountView, onRpc, makeMockEnv } from "@web/../tests/web_test_helpers";
import { mailModels } from "@mail/../tests/mail_test_helpers";
import { click, animationFrame } from "@odoo/hoot-dom";

class Product extends models.Model {
    _name = "product.product";
    name = fields.Char();
    barcode = fields.Char();

    _records = [
        { id: 1, name: "Galaxy S24", barcode: "111222333" },
        { id: 2, name: "Galaxy Tab S9", barcode: "444555666" },
    ];

    _views = {
        kanban: `
            <kanban js_class='product_kanban_catalog'>
                <templates>
                    <t t-name="card">
                        <field name="id"/>
                        <field name="name"/>
                        <div name="o_kanban_price"
                            t-attf-id="product-{{record.id.raw_value}}-price"
                            class="d-flex flex-column"/>
                    </t>
                </templates>
            </kanban>`
    };
}

class SaleOrder extends models.Model {
    _name = "sale.order";
    order_line = fields.One2many({ relation: "sale.order.line" });
    _records = [{ id: 1, order_line: [1] }];
}

class PurchaseOrder extends models.Model {
    _name = "purchase.order";
    order_line = fields.One2many({ relation: "purchase.order.line" });
    _records = [{ id: 1, order_line: [1] }];
}

class SaleOrderLine extends models.Model {
    _name = "sale.order.line";
    id = fields.Integer();
    name = fields.Text();
    product_id = fields.Many2one({ relation: "product.product" });
    product_uom_qty = fields.Float();
    quantity = fields.Float();
    order_id = fields.Many2one({ relation: "sale.order" });

    _records = [{ id: 1, name: "Galaxy S24", product_id: 1, product_uom_qty: 1, order_id: 1 }];
}

class PurchaseOrderLine extends models.Model {
    _name = "purchase.order.line";
    id = fields.Integer();
    name = fields.Text();
    product_id = fields.Many2one({ relation: "product.product" });
    product_qty = fields.Float();
    quantity = fields.Float();
    order_id = fields.Many2one({ relation: "sale.order" });

    _records = [{ id: 1, name: "Galaxy S24", product_id: 1, product_qty: 1, order_id: 1 }];
}

defineModels({ Product, SaleOrder, SaleOrderLine, PurchaseOrderLine, PurchaseOrder, ...mailModels });

test("Updated Quantity of Sale Order", async () => {
    const env = await makeMockEnv();

    onRpc("product.product", "web_search_read", () => ({
        length: 2,
        records: [
            { id: 1, name: "Galaxy S24", barcode: "111222333" },
            { id: 2, name: "Galaxy Tab S9", barcode: "444555666" },
        ],
    }));

    onRpc("/product/catalog/order_lines_info", () => ({
        1: { price: 899, quantity: 1, productType: "consu", readOnly: false },
        2: { price: 1099, quantity: 1, productType: "consu", readOnly: false },
    }));

    onRpc("/product/catalog/update_order_line_info", async (request) => {
        const { params } = await request.json();
        const { product_id, quantity } = params;
        expect.step("update_sale_order_line_info");
        expect(quantity).toBe(2);
        expect(product_id).toBe(1);
        return { price: 899 };
    });

    await mountView({
        resModel: "product.product",
        type: "kanban",
        context: {
            order_id: 1,
            product_catalog_order_model: "sale.order",
        },
    });

    await click(".o_control_panel");
    await animationFrame();

    env.services.barcode.bus.trigger("barcode_scanned", { barcode: "111222333" });
    await animationFrame();

    expect.verifySteps(["update_sale_order_line_info"]);
});

test("Add New Product in Sale Order", async () => {
    const env = await makeMockEnv();

    onRpc("product.product", "web_search_read", () => ({
        length: 2,
        records: [
            { id: 1, name: "Galaxy S24", barcode: "111222333" },
            { id: 2, name: "Galaxy Tab S9", barcode: "444555666" },
        ],
    }));

    onRpc("/product/catalog/order_lines_info", () => ({
        1: { price: 899, quantity: 1, productType: "consu", readOnly: false },
        2: { price: 1099, quantity: 0, productType: "consu", readOnly: false },
    }));

    onRpc("/product/catalog/update_order_line_info", async (request) => {
        const { params } = await request.json();
        const { product_id, quantity } = params;

        expect.step("create_new_sale_order_line");
        expect(product_id).toBe(2);
        expect(quantity).toBe(1);

        return { price: 1099 };
    });

    await mountView({
        resModel: "product.product",
        type: "kanban",
        context: {
            order_id: 1,
            product_catalog_order_model: "sale.order",
        },
    });

    await click(".o_control_panel");
    await animationFrame();

    env.services.barcode.bus.trigger("barcode_scanned", { barcode: "444555666" });
    await animationFrame();

    expect.verifySteps(["create_new_sale_order_line"]);
});

test("Updated Quantity of Purchase Order", async () => {
    const env = await makeMockEnv();

    onRpc("product.product", "web_search_read", () => ({
        length: 2,
        records: [
            { id: 1, name: "Galaxy S24", barcode: "111222333" },
            { id: 2, name: "Galaxy Tab S9", barcode: "444555666" },
        ],
    }));

    onRpc("/product/catalog/order_lines_info", () => ({
        1: { price: 899, quantity: 1, productType: "consu", readOnly: false, uom: { id: 1, name: "Units" } },
        2: { price: 1099, quantity: 1, productType: "consu", readOnly: false, uom: { id: 1, name: "Units" } },
    }));

    onRpc("/product/catalog/update_order_line_info", async (request) => {
        const { params } = await request.json();
        const { product_id, quantity } = params;
        expect.step("update_purchase_order_line_info");
        expect(quantity).toBe(2);
        expect(product_id).toBe(1);
        return { price: 899 };
    });

    await mountView({
        resModel: "product.product",
        type: "kanban",
        context: {
            order_id: 1,
            product_catalog_order_model: "purchase.order",
        },
    });

    await click(".o_control_panel");
    await animationFrame();

    env.services.barcode.bus.trigger("barcode_scanned", { barcode: "111222333" });
    await animationFrame();

    expect.verifySteps(["update_purchase_order_line_info"]);
});

test("Add New Product in Purchase Order", async () => {
    const env = await makeMockEnv();

    onRpc("product.product", "web_search_read", () => ({
        length: 1,
        records: [
            { id: 1, name: "Galaxy S24", barcode: "111222333" },
            { id: 2, name: "Galaxy Tab S9", barcode: "444555666" },
        ],
    }));

    onRpc("/product/catalog/order_lines_info", () => ({
        1: { price: 899, quantity: 1, productType: "consu", readOnly: false, uom: { id: 1, name: "Units" } },
        2: { price: 1099, quantity: 0, productType: "consu", readOnly: false, uom: { id: 1, name: "Units" } },
    }));

    onRpc("/product/catalog/update_order_line_info", async (request) => {
        const { params } = await request.json();
        const { product_id, quantity } = params;

        expect.step("create_new_purchase_order_line");
        expect(product_id).toBe(2);
        expect(quantity).toBe(1);

        return { price: 1099 };
    });

    await mountView({
        resModel: "product.product",
        type: "kanban",
        context: {
            order_id: 1,
            product_catalog_order_model: "purchase.order",
        },
    });

    await click(".o_control_panel");
    await animationFrame();

    env.services.barcode.bus.trigger("barcode_scanned", { barcode: "444555666" });
    await animationFrame();

    expect.verifySteps(["create_new_purchase_order_line"]);
});
