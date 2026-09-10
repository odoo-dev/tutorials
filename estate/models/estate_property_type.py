from odoo import fields, models


class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Estate Property Type'
    _rec_name = 'property_type'

    property_type = fields.Char(required=True)
