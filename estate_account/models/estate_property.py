from odoo import Command, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round


class EstatePropertyModel(models.Model):
    _inherit = "estate_property"

    def action_set_property_sold(self):
        for record in self:
            journal = self.env["account.journal"].sudo().search([
                *self.env["account.journal"].sudo()._check_company_domain(self.env.company),
                ("type", "=", "sale"),
            ], limit=1)
            
            precision_digits = self.env["decimal.precision"].precision_get("Account")
            invoice_vals = {
                'partner_id': record.buyer_id.id,
                'move_type': 'out_invoice',
                'journal_id': journal.id,
                'line_ids': [
                    Command.create({
                        'name': 'Down Payment',
                        'quantity': 1,
                        'price_unit': float_round(record.selling_price * 0.06, precision_digits=precision_digits)
                    }),
                    Command.create({
                        'name': 'Administrative Fees',
                        'quantity': 1,
                        'price_unit': 100.00
                    }),
                ]
            }

            print("Method from inherited model called from Estate Account module")
            print(f"Journal values:${invoice_vals}")

            self.check_access('write')
            print(" reached ".center(100, '='))
            self.env["account.move"].sudo().create(invoice_vals)

        return super().action_set_property_sold()