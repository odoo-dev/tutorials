from odoo import api, fields, models, Command
from odoo.tools.float_utils import float_round

class EstateProperty(models.Model):
    _inherit = "estate.property"

    def mark_as_sold(self):

        # Seems not needed?
        # journal = self.env["account.journal"].sudo().search([
        #     *self.env["account.journal"].sudo()._check_company_domain(self.env.company),
        #     ("type", "=", "sale"),
        # ], limit=1)

        move_val = {
            'partner_id': self.buyer_id.id,
            'move_type': 'out_invoice',
            "invoice_line_ids": [
                Command.create({
                    "name": self.name,
                    "quantity": 1,
                    "price_unit": float_round(0.06 * self.selling_price, precision_digits=2)
                }),
                Command.create({
                    "name": "Administrative fees",
                    "quantity": 1,
                    "price_unit": 100.00
                }),

            ]
        }

        self.env['account.move'].create(move_val)

        # This should be print whenever a sold button action is triggered.
        # print('mark as sold method is successfully inherited!')        

        return super().mark_as_sold()