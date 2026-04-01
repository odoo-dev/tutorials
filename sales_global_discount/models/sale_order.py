from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = "sale.order"

    global_discount_percentage = fields.Float(
        string="Global Discount Percentage",
        copy=False,
    )

    def global_discount_lines(self):
        self.ensure_one()
        return self.order_line.filtered(lambda l: l._is_global_discount())

    def real_product_lines(self):
        self.ensure_one()
        return self.order_line.filtered(
            lambda l: (not l.display_type) and (not l._is_global_discount())
        )

    def sync_global_discount_lines(self):
        for order in self:
            remaining = order.real_product_lines()
            discount_lines = order.global_discount_lines()

            if not remaining:
                discount_lines.unlink()
                order.global_discount_percentage = 0.0
                continue

            discount_lines.unlink()

            wizard = self.env["sale.order.discount"].with_context(
                active_model="sale.order",
                active_id=order.id,
            ).create({
                "sale_order_id": order.id,
                "discount_type": "so_discount",
                "discount_percentage": order.global_discount_percentage,
            })
            wizard.action_apply_discount()
