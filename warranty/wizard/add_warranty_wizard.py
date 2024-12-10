from odoo import api, fields, models, Command


class AddWarrantyWizard(models.TransientModel):
    _name = "add.warranty.wizard"
    warranty_line_ids = fields.One2many("add.warranty.line", "warranty_id")
    sale_order_id = fields.Many2one("sale.order", string="sale order id")

    @api.model
    def default_get(self, fields_list):
        res = super(AddWarrantyWizard, self).default_get(fields_list)
        sale_order_id = self.env.context.get("active_id")
        sale_order = self.env["sale.order"].browse(sale_order_id)

        warranty_line_vals = []
        for line in sale_order.order_line:
            if line.product_template_id.warranty:
                warranty_line_vals.append(
                    Command.create(
                        {
                            "sale_order_line_id": line.id,
                            "product_id": line.product_template_id,
                        }
                    )
                )
        res["warranty_line_ids"] = warranty_line_vals
        return res

    def add_warranty_action(self):
        warranty_line_list = []
        for line in self.warranty_line_ids:
            price = line.sale_order_line_id.price_subtotal * (
                line.warranty_config_id.percentage / 100
            )
            warranty_line_list.append(
                {
                    "order_id": line.sale_order_line_id.order_id.id,
                    "product_id": line.warranty_config_id.product_id.id,
                    "price_unit": price,
                    "warranty_sale_order_line_id": line.sale_order_line_id.id,
                }
            )
        if warranty_line_list:
            self.env["sale.order.line"].create(warranty_line_list)
        return {"type": "ir.actions.act_window_close"}
