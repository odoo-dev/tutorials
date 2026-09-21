from odoo import models, fields


class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = "Property Type"
    _order = 'sequence, name'

    name = fields.Char(required=True)
    property_ids = fields.One2many(
        'estate.property',
        'property_type_id'
    )
    sequence = fields.Integer()

    _name_unique = models.Constraint(
        'UNIQUE(name)',
        "Property type name must be unique",
    )
