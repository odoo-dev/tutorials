from odoo import fields, models

class estatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Estate property type model"

    name = fields.Char(required=True, string='Name')
