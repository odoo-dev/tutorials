from odoo import models, fields


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Real Estate Property Type"

    name = fields.Char(required=True)

    _unique_name = models.Constraint(
        "UNIQUE(name)",
        "The name of the property type must be unique",
    )
