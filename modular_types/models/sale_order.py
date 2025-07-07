from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        self.ensure_one()
        res = super().action_confirm()

        for manufacturing_order in self.mrp_production_ids:
            sale_order_line = self.order_line.filtered(
                lambda line: line.product_id == manufacturing_order.product_id
                and line.product_uom_qty == manufacturing_order.product_qty
            )

            for move_line in manufacturing_order.move_raw_ids.filtered(
                lambda move: move.modular_type_id
            ):
                modular_type_value = sale_order_line.modular_type_value_ids.filtered(
                    lambda m: m.modular_type_id == move_line.modular_type_id
                ).value

                move_line.product_uom_qty *= modular_type_value

        return res
