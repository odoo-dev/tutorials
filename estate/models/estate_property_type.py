from odoo import fields, models


class PropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Estate property type"
    _order = "sequence, name"

    name = fields.Char(required=True)
    property_ids = fields.One2many("estate.property", "property_type_id", "Property")
    sequence = fields.Integer("Sequence", default=1)

    _uniq_name = models.Constraint(
        'UNIQUE(name)',
        "This type name is already taken"
    )
