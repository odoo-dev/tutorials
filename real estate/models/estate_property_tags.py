# -*- coding: utf-8 -*-

from odoo import models,fields

class estate_property_tags(models.Model):
    _name = "estate.property.tag"
    _description = "tags directory for estate property"
    _order = "name"

    name = fields.Char(string="Name", required=True)
    color = fields.Integer(string="Color")

    _sql_constraints = [
        (
            "tag_name_uniq",
            "UNIQUE(name)",
            "Tag name must be unique"
        )
    ]
