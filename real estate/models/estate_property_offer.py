# -*- coding: utf-8 -*-

from odoo import models, fields

class estate_property_offer(models.Model):
    _name="estate.property.offer"
    _description="Offer table for estate property"

    price = fields.Float(string="Price")
    status = fields.Selection(string="Status", 
        selection=[("accepted", "Accepted"), ("refused", "Refused")], 
        copy=False
    )
    partner_id = fields.Many2one(string="Partner", comodel_name="res.partner", required=True)
    property_id = fields.Many2one(string="Property", comodel_name="estate.property", required=True)
    