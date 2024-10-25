from odoo import fields, models, Command

class estateProperty(models.Model):

    _inherit = 'estate.property'

    def action_sold(self):
        supper_call = super().action_sold()

        invoice_price = {
            "name": self.name,
            "quantity": 1,
            "price_unit": self.selling_price * 1.06
        }

        invoice_administrative_fees = {
            "name": "Administrative Fees",
            "quantity": 1,
            "price_unit": 100.00
        }

        self.env["account.move"].create({
            "name": self.name + " Invoice",
            "partner_id": self.buyer_id.id,
            "move_type": "out_invoice",
            "invoice_line_ids": [
                Command.create(invoice_price),
                Command.create(invoice_administrative_fees)
            ]
        }) 

        return supper_call