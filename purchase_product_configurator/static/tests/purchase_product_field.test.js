import { test, expect } from "@odoo/hoot";
import { edit, press, click, animationFrame } from "@odoo/hoot-dom";
import { defineModels, models, fields, onRpc, mountView } from "@web/../tests/web_test_helpers";
import { mailModels } from "@mail/../tests/mail_test_helpers";

class PurchaseOrder extends models.Model {
    _name = "purchase.order";
    id = fields.Integer();
    display_name = fields.Char({ string: "Displayed name" });
    order_line = fields.One2many({ string: "Order lines", relation: "purchase.order.line", relation_field: "order_id" });

    _records = [
        { id: 1, display_name: "first record", order_line: [] }
    ];
}

class PurchaseOrderLine extends models.Model {
    _name = "purchase.order.line";
    id = fields.Integer();
    order_id = fields.Many2one({ string: "Order Reference", relation: "purchase.order" });
    configurable_product_template_id = fields.Many2one({ string: "Product", relation: "product.template" });
    product_id = fields.Many2one({ string: "Product", relation: "product.product" });
    name = fields.Char({ string: "Description" });

    _records = [];
}

class ProductTemplate extends models.Model {
    _name = "product.template";
    id = fields.Integer();
    display_name = fields.Char({ string: "Partner Type" });
    name = fields.Char({ string: "Partner Type" });

    _records = [
        { id: 1, display_name: 'desk' }
    ];

    get_single_product_variant() {
        return Promise.resolve({ product_id: 14, product_name: 'desk' });
    }
}

class ProductProduct extends models.Model {
    _name = "product.product";
    id = fields.Integer();
    display_name = fields.Char({ string: "Partner Type" });
    name = fields.Char({ string: "Partner Type" });

    _records = [
        { id: 14, display_name: 'desk' }
    ];
}

defineModels({...mailModels, PurchaseOrder, PurchaseOrderLine, ProductTemplate, ProductProduct});

test("pressing tab with incomplete text will create a product", async () => {

    const rpcCalls = [];

    onRpc((params) => {
        rpcCalls.push(params);
    });

    await mountView({
        resModel: "purchase.order",
        type: "form",
        arch: `
            <form>
                <sheet>
                    <field name="order_line">
                        <list editable="bottom">
                            <field name="configurable_product_template_id" widget="pol_product_variant_many2one"/>
                            <field name="product_id" optional="hide"/>
                            <field name="name" optional="show"/>
                        </list>
                    </field>
                </sheet>
            </form>`
    });

    await click("a");
    await animationFrame();
    await click(".o-autocomplete--input");
    await edit("new product");
    await animationFrame();
    await press("tab");

    expect(rpcCalls.some(call => call.method === "get_views")).toBe(true);
    expect(rpcCalls.some(call => call.method === "onchange")).toBe(true);
    expect(rpcCalls.some(call => call.method === "onchange")).toBe(true);
    expect(rpcCalls.some(call => call.method === "name_search")).toBe(true);
    expect(rpcCalls.some(call => call.method === "name_search")).toBe(true);
});
