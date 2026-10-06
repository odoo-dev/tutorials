from odoo import models
from odoo.orm.commands import Command


class EstateAccount(models.Model):
    _inherit = "estate.property"

    def set_sold(self):
        check_sold = super().set_sold()
        if check_sold:
            self.env["account.move"].create({
                    "partner_id": self.buyer_id.id,
                    "move_type": "out_invoice",
                    "invoice_line_ids": [
                        Command.create({
                                "name": "6% of Selling Price",
                                "quantity": 1,
                                "price_unit": self.selling_price * 0.06,
                            }),
                        Command.create({
                                "name": "Administrative Fees",
                                "quantity": 1,
                                "price_unit": 100,
                            }),
                    ],
                })
        return check_sold
