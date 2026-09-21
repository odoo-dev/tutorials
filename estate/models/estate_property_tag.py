from odoo import fields, models


class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "This is the tag of property"

    name = fields.Char(required=True)

    _unique_import_id = models.Constraint(
        'unique (name)',
        "This name is already taken",
    )
