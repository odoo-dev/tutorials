from odoo import fields,models
class AddOfferWizard(models.TransientModel):
    _name='estate.property.add.offer.wizard'
    price = fields.Float(required=True)
    partner_id=fields.Many2one('res.partner',string='Partner',  required=True)
    validity= fields.Integer(default=7)

    def add_offer_action(self):
        property_ids = self.env.context.get("default_property_ids", [])
        for property_id in property_ids:
            self.env['estate.property.offer'].create({
                'price': self.price,
                'validity': self.validity,
                'partner_id': self.partner_id.id,
                'property_id': property_id,  
            })
        return {'type': 'ir.actions.act_window_close'}         



      