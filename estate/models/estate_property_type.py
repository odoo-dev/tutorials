from odoo import fields, models


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Estate Property Type"

    name = fields.Char(required=True)

    _check_unique_type = models.Constraint(
        'UNIQUE(name)',
        'A property type with that name already exists.'
    )
