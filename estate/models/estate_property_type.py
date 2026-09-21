from odoo import fields, models


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "This is the type of property (House, Apartment, Studio, etc.)"

    name = fields.Char(required=True)

    _unique_import_id = models.Constraint(
        'unique (name)',
        "This name is already taken",
    )
