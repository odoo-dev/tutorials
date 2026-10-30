from odoo import Command, models


class EstateProperty(models.Model):
    _name = 'estate.property'
    _inherit = ["estate.property"]

    def action_sold(self):
        journal = self.env["account.journal"].sudo().search(
            [("type", "=", "sale")], limit=1)
        for property in self:
            self.env["account.move"].sudo().create({
                "partner_id": property.buyer.id,
                "move_type": "out_invoice",
                "journal_id": journal.id,
                "line_ids": [
                    Command.create({
                        "name": "Commission",
                        "quantity": 1.0,
                        "price_unit": property.selling_price * 0.06
                    }),
                    Command.create({
                        "name": "Additional administrative fees",
                        "quantity": 1.0,
                        "price_unit": 100.0
                    })
                ]
            })
        return super().action_sold()
