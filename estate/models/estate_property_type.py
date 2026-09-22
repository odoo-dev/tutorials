from odoo import fields, models


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Test property type description"
    _order = "sequence"

    name = fields.Char(required=True)
    property_ids = fields.One2many("estate.property", "property_type_id", string="Properties")
    sequence = fields.Integer('Sequence', default=1)

    _unique_property_type_name = models.Constraint(
        'UNIQUE(name)',
        'The property type name must be unique.'
    )
