from odoo import fields, models


class PropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Estate property type"

    name = fields.Char(required=True)

    _uniq_name = models.Constraint(
        'UNIQUE(name)',
        "This type name is already taken"
    )
