import { expect, test } from "@odoo/hoot";
import { defineModels, fields, makeMockEnv, models, mountView, onRpc } from "@web/../tests/web_test_helpers";
import { mailModels } from "@mail/../tests/mail_test_helpers";
import { animationFrame, click, press } from "@odoo/hoot-dom";

async function simulateBarCode(barcode) {
    for (const code of barcode) {
        await press(code);
    }
}

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
            </kanban>
        `,
    };
}

class SaleOrder extends models.Model {
    _name = "sale.order";

    order_line = fields.One2many({ relation: "sale.order.line" });

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

defineModels({ Product, SaleOrder, SaleOrderLine, ...mailModels });

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

test("Add New Product in Sale Order", async () => {
    const env = await makeMockEnv();

    onRpc("/product/catalog/update_order_line_info", async (request) => {
        const { params } = await request.json();
        const { product_id, quantity } = params;

        expect.step("create_new_sale_order_line");
        expect(product_id).toBe(2, {
            message: "Expected product_id to be 2 (Galaxy Tab S9) when scanning barcode '444555666'.",
        });
        expect(quantity).toBe(1, {
            message: "Expected quantity to be 1 when adding a new product to the sale order.",
        });

        return {};
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

    await simulateBarCode(["4","4","4","5","5","5","6","6","6", "Enter"]);
    await animationFrame();

    expect.verifySteps(["create_new_sale_order_line"]);
});

test("Updated Quantity of Sale Order", async () => {
    const env = await makeMockEnv();

    onRpc("/product/catalog/update_order_line_info", async (request) => {
        const { params } = await request.json();
        const { product_id, quantity } = params;

        expect.step("update_sale_order_line_info");
        expect(product_id).toBe(1, {
            message: "Expected product_id to be 1 (Galaxy S24) when scanning barcode '111222333'.",
        });
        expect(quantity).toBe(2, {
            message: "Expected the quantity to increase to 2 when scanning the same product again.",
        });

        return {};
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

    await simulateBarCode(["1","1","1","2","2","2","3","3","3", "Enter"]);
    await animationFrame();

    expect.verifySteps(["update_sale_order_line_info"]);
});
