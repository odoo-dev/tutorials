from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    is_deposit_line = fields.Boolean(default=False)
    linked_line_id = fields.Many2one("sale.order.line", ondelete="cascade")

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        for line in lines:
            if line.product_id.require_deposit and not line.is_deposit_line:
                line._create_deposit_line()
        return lines

    def write(self, vals):
        res = super().write(vals)
        if "product_uom_qty" in vals:
            for line in self:
                deposit_line = self.env["sale.order.line"].search(
                    [("linked_line_id", "=", line.id)], limit=1
                )
                if deposit_line:
                    deposit_line.write({"product_uom_qty": vals["product_uom_qty"]})
        return res

    def _create_deposit_line(self):
        deposit_product_id = self.env["ir.config_parameter"].get_param(
            "rental.deposit_product_id"
        )
        if not deposit_product_id:
            return
        self.env["sale.order.line"].create(
            {
                "order_id": self.order_id.id,
                "product_id": int(deposit_product_id),
                "name": f"Deposit for {self.product_id.name}",
                "product_uom_qty": self.product_uom_qty,
                "price_unit": self.product_id.deposit_amount,
                "is_deposit_line": True,
                "linked_line_id": self.id,
            }
        )
