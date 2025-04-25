from odoo import fields, models


class EstatePropertyTypeModel(models.Model):
    _name = "estate_property_type"
    _description = "Real estate property type"

    name = fields.Char(required=True)