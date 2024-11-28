from odoo import models, fields, api, Command
class InheritedPropertyEstate(models.Model):
    _inherit="estate.property"
    invoice_line_ids = fields.One2many('account.move','partner_id')
    quantity=fields.Integer(string="Quantity")
    #override method action_do_sold
    def action_do_sold(self):        
        moves=super().action_do_sold()
        move_values = {
            'partner_id': self.partner_id.id,  
            'move_type': 'out_invoice',
             "invoice_line_ids": [
                Command.create({
                    "name":self.name,
                    "quantity": 1,
                    "price_unit": self.selling_price,
                }),
                Command.create({
                    "name": "Administrative fees",
                    "quantity": 1,
                    "price_unit": 100.00,
                }),
                ]
            }
        account_move = self.env['account.move'].sudo().create(move_values)
        return moves

        
    

        