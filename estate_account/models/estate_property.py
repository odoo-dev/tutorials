from odoo import models, Command


class EstateProperty(models.Model):
    _inherit = "estate.property"

    def action_sold(self):
        self.check_access_rights('write')
        self.check_access_rule('write')
        self.env["account.move"].sudo().create(
            {
                "move_type": "out_invoice",
                "partner_id": self.buyer_id.id,
                "invoice_line_ids": [
                    Command.create({'name': '6% of the selling price', 'quantity': 1, 'price_unit': 0.06 * self.selling_price}),
                    Command.create({'name': 'Administrative Fees', 'quantity': 1, 'price_unit': 100.00}),
                ],
            }
        )
        return super().action_sold()
