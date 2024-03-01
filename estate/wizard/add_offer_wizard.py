# -*- coding: utf-8 -*-

from odoo import models, fields

class AddOffer(models.TransientModel):
    _name = "estate.add.offer"
    _description = "model to add offer to multiple properties"

    price = fields.Integer(string="Price")
    buyer_id = fields.Many2one(string="Buyer", comodel_name="res.partner")
    validity = fields.Integer(string="Number of days")
    property_id = fields.Many2one(string="Property", comodel_name="estate.property")

    def action_add_offer(self):
            active_ids = self.env.context.get("active_ids") 
            for p_id in active_ids:
                estate_property = self.env['estate.property'].browse(p_id)
                estate_property.offer_ids.create(
                    {
                        "price" : self.price,
                        "partner_id" : self.buyer_id.id,
                        "property_id" : p_id,
                        "validity" : self.validity
                    }
                )