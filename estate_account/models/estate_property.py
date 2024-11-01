from odoo import models, Command


class estateProperty(models.Model):
    _inherit = ['estate.property']

    def action_sold(self):
        # invoice_values = {
        #     'partner_id' : self.buyer_id.id,
        #     'move_type' : 'out_invoice'
        # }

        selling_price = self.selling_price
        invoice_lines = [
            Command.create({'name': self.name, 'price_unit': selling_price, 'quantity': 1}),
            Command.create({'name': 'Extra fees', 'price_unit': 100, 'quantity': 1})
        ]
        invoice_values = {
            'partner_id': self.buyer_id.id,
            'move_type': 'out_invoice',
            'invoice_line_ids': invoice_lines,
        }
        # print(" reached ".center(100, '='))
        # print(self.env['account.move'].check_access_rights('write'))
        # print(self.env['account.move'].check_access_rule('write'))
        self.env['account.move'].sudo().create(invoice_values)
        return super().action_sold()
