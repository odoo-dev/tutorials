from odoo import models, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.ondelete(at_uninstall=False)
    def _ondelete_sync_global_discount(self):
        orders = self.mapped("order_id")

        deleted_real_line = any(
            (not l.display_type) and (not l._is_global_discount())
            for l in self
        )

        if not deleted_real_line:
            return

        for order in orders:
            if order.state not in ("draft", "sent"):
                continue
            if order.global_discount_percentage:
                order.sync_global_discount_lines()