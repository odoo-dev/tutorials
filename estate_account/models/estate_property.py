from odoo import Command,models,fields

class EstateProperty(models.Model):
    _description = "Estate Account property Model"
    _inherit="estate.property"
    invoice_line_ids = fields.One2many('account.move','property_id')
    quantity=fields.Integer(string="Quantity")
    
    def action_sell_property(self):
        # self.env['account.move'].check_access_rights('create')
        move_values = {
            'partner_id': self.buyer.id,  
            'move_type': 'out_invoice',
            'property_id':self.id,
            'invoice_line_ids': [
                Command.create({
                    "name":self.name,
                    "quantity": 1,
                    "price_unit": 0.6 * self.selling_price, # 6% of the S.P
                }),
                
                Command.create({
                    "name": "Administrative fees",
                    "quantity": 1,
                    "price_unit": 100.00,
                }),
            ]
        }
        # print(" reached ".center(100, '='))
        self.env['account.move'].sudo().create(move_values)
        
        return super().action_sell_property()