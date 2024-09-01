from odoo import Command, models


class EstateProperty(models.Model):
    _inherit = "estate.property"

    def set_state_sold(self):
        super_call = super().set_state_sold()

        invoice_line_purchase = {
            "name": self.name,
            "quantity": 1,
            "price_unit": self.selling_price * 1.06,
        }

        invoice_line_adminstrative_fees = {
            "name": "Adminstrative Fees",
            "quantity": 1,
            "price_unit": 100.00,
        }

        self.env["account.move"].create({
            "name": self.name + " Purchase Invoice",
            "partner_id": self.buyer_id.id,
            "move_type": "out_invoice",
            "invoice_line_ids": [
                Command.create(invoice_line_purchase),
                Command.create(invoice_line_adminstrative_fees),
            ]
        })

        return super_call
