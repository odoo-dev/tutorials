# 19.0-tutorials-frtan

from odoo import Command, models

class EstateProperty(models.Model):
    _inherit = 'estate.property'

    def action_sold_estate_property(self):
        res = []
        for record in self:
            res.append({
                'partner_id': record.buyer_id.id, # idk why it has to get the id, i thought buyer_id = id
                'move_type': 'out_invoice',
                'invoice_line_ids': [
                    Command.create({ # this does not need brackets [] (expects a dict, not list[dict])
                        # 'move_id': supposedly this.id but not needed due to Command
                        'name': record.name,
                        'quantity': 1,
                        'price_unit': 0.06 * record.selling_price,
                    }),
                    Command.create({
                        'name': 'Administrative Fees',
                        'quantity': 1,
                        'price_unit': 100,
                    })
                ]
            })
        self.env['account.move'].create(res)
        return super().action_sold_estate_property()