from odoo import fields,models,api

class EstatePropertyOfferWizard(models.TransientModel):
    _name = "estate.property.offer.wizard"
    _description = "This wizard will add offers on the fly"

    offered_price = fields.Float(string="Offered Price")
    validity = fields.Integer(string="Validity", default=7)
    partner_id = fields.Many2one("res.partner", string="Partner", required=True)

    def make_offer(self):
        active_property_ids = self.env['estate.property'].browse(self._context.get('active_ids'))
        offer_list = []
        for record in active_property_ids:
            offer_vals = {
                'property_id': record.id,
                'partner_id': self.partner_id.id,
                'price': self.offered_price,
                'validity': self.validity,
            }
            offer_list.append(offer_vals)
        self.env['estate.property.offer'].create(offer_list)
