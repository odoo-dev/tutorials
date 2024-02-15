# -*- coding: utf-8 -*-

from odoo import models,fields

class estate_property_tags(models.Model):
    _name = "estate.property.tag"
    _description = "tags directory for estate property"

    name = fields.Char(string="Name", required=True)
