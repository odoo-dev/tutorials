# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class KitSubProductWizard(models.TransientModel):
    _name = "kit.sub.product.wizard"
    _description = "Kit Sub Product Wizard"

    order_line_id = fields.Many2one("sale.order.line", string="Sale Order Line")
    line_ids = fields.One2many("kit.sub.product.wizard.line", "wizard_id", string="Sub Products")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        order_line = self.env["sale.order.line"].browse(self.env.context.get("default_order_line_id"))
        if order_line and order_line.product_id.is_kit:
            existing_so_lines = self.env["sale.order.line"].search([
                ("order_id", "=", order_line.order_id.id),
                ("is_sub_product_line", "=", True),
                ("parent_line_id", "=", order_line.id),
            ])
            if existing_so_lines:
                existing_lines = []
                for so_line in existing_so_lines:
                    existing_lines.append((0, 0, {
                            "product_id": so_line.product_id.id,
                            "quantity": so_line.product_uom_qty,
                            "price_unit": so_line.wizard_price_unit
                            or so_line.product_id.lst_price,
                        })
                    )
                res["line_ids"] = existing_lines
            else:
                lines = []
                for prod in order_line.product_id.kit_product_ids:
                    lines.append((0, 0, {
                        "product_id": prod.id,
                        "quantity": 1.0,
                        "price_unit": prod.lst_price,
                    }))
                res["line_ids"] = lines
        return res

    def action_confirm(self):
        order = self.order_line_id.order_id
        total_price = 0.0
        for line in self.line_ids:
            total_price += line.price_unit * line.quantity
            existing_so_line = self.env["sale.order.line"].search([
                    ("order_id", "=", order.id),
                    ("product_id", "=", line.product_id.id),
                    ("is_sub_product_line", "=", True),
                    ("parent_line_id", "=", self.order_line_id.id),
                ], limit=1)
            if existing_so_line:
                existing_so_line.write({
                    "product_uom_qty": line.quantity,
                    "price_unit": 0.0,
                    "wizard_price_unit": line.price_unit,
                    "name": line.product_id.name,
                })
            else:
                self.env["sale.order.line"].create({
                    "order_id": self.order_line_id.order_id.id,
                    "product_id": line.product_id.id,
                    "product_uom_qty": line.quantity,
                    "price_unit": 0.0,
                    "product_uom": line.product_id.uom_id.id,
                    "is_sub_product_line": True,
                    "name": line.product_id.name,
                    "is_kit_component": True,
                    "parent_line_id": self.order_line_id.id,
                    "wizard_price_unit": line.price_unit,
                })
        self.order_line_id.write({"price_unit": total_price + self.order_line_id.price_unit})
