from odoo import Command, models


class Property(models.Model):
    _inherit = "estate.property"

    def action_sell_property(self):
        for record in self:
            self.env["account.move"].create(
                {
                    "partner_id": record.partner_id.id,
                    "move_type": "out_invoice",
                    "invoice_line_ids": [
                        Command.create(
                            {
                                "name": record.name,
                                "quantity": 1,
                                "price_unit": record.selling_price * 0.06,
                            }
                        ),
                        Command.create(
                            {
                                "name": "administrative fees",
                                "price_unit": 100.00,
                            }
                        ),
                    ],
                }
            )
        return super().action_sell_property()
