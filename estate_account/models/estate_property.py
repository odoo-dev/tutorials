from odoo import fields, models, Command

class EstateProperty(models.Model):
    _inherit = "estate.property"

    #action methods
    def sold_state(self):
        res = super().sold_state()

        for record in self:
            self.env['account.move'].create([{
                "partner_id" : record.buyer_id.id,
                "move_type" : "out_invoice",
                "invoice_line_ids" : [
                    Command.create({'name': record.name, 'quantity': 1.0, 'price_unit': record.selling_price * 6.0/100.0}),
                    Command.create({'name': 'Administrative Fees', 'quantity': 1.0, 'price_unit': 100.0})
                ]
            }])
        return res
