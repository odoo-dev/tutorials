from odoo import fields, models


class SalesOrderLine(models.Model):
    _inherit = "sale.order.line"

    def is_discount_line(self):
        discountProduct = self.order_id.env["product.product"].search(
            [("name", "=", "Discount")], limit=1
        )
        return self.product_id == discountProduct

    def unlink(self):
        order_ids = self.mapped("order_id")
        result = super().unlink()

        for order in order_ids:
            order._update_discount()

        return result

    def create(self, vals):
        line = super().create(vals)

        if line.order_id and not line.is_discount_line():
            line.order_id._updateDiscount()

        return line
