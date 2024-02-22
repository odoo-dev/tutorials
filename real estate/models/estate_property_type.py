# -*- coding: utf-8 -*-

from odoo import models, fields, api

class estate_property_type(models.Model):
    _name = "estate.property.type"
    _description = "Types of estate properties"
    _order = "sequence, name"

    name = fields.Char(string="name", required=True)
    property_ids = fields.One2many(string="Properties", comodel_name="estate.property", inverse_name="property_type_id")
    sequence = fields.Integer(string="Sequence", default=10)
    offer_ids = fields.One2many(string="Offers", comodel_name="estate.property.offer", inverse_name="property_type_id")
    offer_count = fields.Integer(string="Offer Count", compute="_compute_offer_count")
    
    _sql_constraints = [
        (
            "type_name_uniq",
            "UNIQUE(name)",
            "Type name must be unique"
        )
    ]

    @api.depends("offer_ids")
    def _compute_offer_count(self):
            self.offer_count = len(self.offer_ids)