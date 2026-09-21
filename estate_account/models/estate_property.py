from pprint import pprint
from typing import override

from odoo import models, fields, Command
from odoo.http import UserError


# invoice_dict['invoice_line_ids'] = [
#     Command.create({
#         'name': 'Property price',
#         'quantity': 1,
#         'price_unit': offer.price,
#     }),
#     Command.create({
#         'name': 'Taxes',
#         'quantity': 1,
#         'price_unit': 0.06 * offer.price,
#     }),
#     Command.create({
#         'name': 'Administrative fees',
#         'quantity': 1,
#         'price_unit': 100000,
#     }),
# ]
class EstateProperty(models.Model):
    _inherit = "estate.property"

    def _create_invoice(self):
        to_invoice = []
        for record in self:
            accepted_offers = record.offer_ids.filtered(lambda o: o.status == 'accepted')
            if len(accepted_offers) != 1:
                raise UserError(("You have to accept exactly one offer to be able to sell(invoice) property"))
            offer = accepted_offers[0]

            invoice_dict = {}
            invoice_dict['partner_id'] = offer.partner_id.id
            invoice_dict['move_type'] = 'out_invoice'
            invoice_dict['journal_id'] = self.env['account.journal'].search([ ('type', '=', 'sale'), ('company_id', '=', self.env.company.id)], limit=1).id
            invoice_dict['invoice_line_ids'] = [
                Command.create({
                    'name': 'Property price',
                    'quantity': 1,
                    'price_unit': offer.price,
                }),
                Command.create({
                    'name': 'Taxes',
                    'quantity': 1,
                    'price_unit': 0.06 * offer.price,
                }),
                Command.create({
                    'name': 'Administrative fees',
                    'quantity': 1,
                    'price_unit': 100000,
                }),
            ]
            to_invoice.append(invoice_dict)
        # debug
        moves = self.env['account.move'].sudo().with_context(default_move_type='out_invoice').create(to_invoice)
        return moves

    def action_sell(self):
        print("OVERRIDE")
        self._create_invoice()
        return super().action_sell()
