from odoo import models,fields

class EstatePropertyOfferWizard(models.TransientModel):
    _name = 'estate.property.offer.wizard'
    _description = 'model.technical.name'
    
    price = fields.Float(required=True)
    partner_id = fields.Many2one("res.partner")
    validity = fields.Integer(default=7)
    
    def make_multiple_offers(self):
        property_ids = self.env.context.get("default_property_ids", [])
        
        if (len(property_ids) > 0):
            for property_id in property_ids:
                
                # Create the offer
                self.env["estate.property.offer"].create({
                    'price': self.price,
                    'validity': self.validity,
                    'partner_id': self.partner_id.id,
                    'property_id': property_id,
                })
        return {'type': 'ir.actions.act_window_close'}  