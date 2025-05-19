from odoo import Command, models


class EstateProperty(models.Model):
    _inherit = ['estate.property']

    def action_set_sold(self):
        res = super().action_set_sold()
        for record in self:
            record.check_access('write')
            # print(" reached ".center(100, '='))
            self.sudo().env['account.move'].create({
                'partner_id': record.buyer_id.id,
                'move_type': 'out_invoice',
                'invoice_line_ids': [
                    Command.create({
                        'name': record.name,
                        'quantity': 1,
                        'price_unit': (0.06 * record.selling_price)
                    }),
                    Command.create({
                        'name': 'Administrative fee',
                        'quantity': 1,
                        'price_unit': 100.00
                    }),
                ]
            })
        return res
