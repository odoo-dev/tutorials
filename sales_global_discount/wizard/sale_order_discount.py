from odoo import models


class SaleOrderDiscount(models.TransientModel):
    _inherit = "sale.order.discount"

    def action_apply_discount(self):
        self.ensure_one()
        order = self.sale_order_id

        if self.discount_type == "so_discount":
            order.order_line.filtered(lambda l: l._is_global_discount()).unlink()

            res = super().action_apply_discount()
            order.global_discount_percentage = self.discount_percentage
            return res

        return super().action_apply_discount()
