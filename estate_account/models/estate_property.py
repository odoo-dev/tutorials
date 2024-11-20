from odoo import models, Command


class InheritedEstateProperty(models.Model):
    _inherit = 'estate.property'

    def action_set_sold(self):
        for record in self:
            self.env['account.move'].create({
                'partner_id': record.buyer_id.id,
                'move_type': 'out_invoice',
                'invoice_line_ids':
                    [
                        Command.create({
                            'name': record.name,
                            'price_unit': 0.06 * record.selling_price,
                            'quantity': 1
                        }),
                        Command.create({
                            'name': 'administrative fees',
                            'price_unit': 100,
                            'quantity': 1
                        })
                    ],
            }
            )
        return super().action_set_sold()
