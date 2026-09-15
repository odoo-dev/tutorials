from odoo import fields, models


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Test property type description"

    name = fields.Char(required=True)

    _unique_property_type_name = models.Constraint(
        'UNIQUE(name)',
        'The property type name must be unique.'
    )
