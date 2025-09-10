from odoo import api, fields, models, Command
from odoo.exceptions import AccessError, UserError, ValidationError


class EstateProperty(models.Model):
    _inherit = "estate.property"

    def action_sold(self):

        invoice_vals = {
            'partner_id': self.buyer_id.id,
            'move_type': 'out_invoice',
            'user_id': self.salesperson_id.id,
            "invoice_line_ids": [
                Command.create({
                    'name': f"6% Payment for Property: {self.name}",
                    'quantity': 1,
                    'price_unit': self.selling_price * 0.06,
                }),
                Command.create({
                    'name': "Admin Fee",
                    'quantity': 1,
                    'price_unit': 100,
                })
            ]
        }

        # print(" reached ".center(100, '='))
        self.env['estate.property'].check_access('write')
        self.env['account.move'].sudo().create(invoice_vals)

        return super().action_sold()
