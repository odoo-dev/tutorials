from odoo import models, Command


class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'Estate Property'
    _inherit = ['estate.property']

    def action_sold(self):
        self.env['account.move'].sudo().with_context(default_move_type='out_invoice').create({
            'name': self.name,
            'partner_id': self.partner_id.id,
            "line_ids": [
                Command.create({
                    'name': 'Down Payment for ' + self.name,
                    'quantity': 0.06,
                    'price_unit': self.selling_price,
                }),
                Command.create({
                    'name': 'Administration Fees',
                    'quantity': 1,
                    'price_unit': 100,
                }),
            ],
        })
        return super().action_sold()
