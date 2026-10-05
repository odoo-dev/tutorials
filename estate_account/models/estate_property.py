from odoo import models, Command


class EstateAccount(models.Model):
    _inherit = "estate.property"

    def set_sold(self):
        res = super().set_sold()
        for record in self:
            self.env["account.move"].create({
                "partner_id": self.buyer_id.id,
                "move_type": "out_invoice",
                "invoice_line_ids": [
                    Command.create({
                        "name": "6% of selling price",
                        "quantity": 1,
                        "price_unit": record.selling_price * 0.06,
                    }),
                    Command.create({
                        "name": "Administrative Fees",
                        "quantity": 1,
                        "price_unit": 100,
                    })
                ]
            })
        return res
