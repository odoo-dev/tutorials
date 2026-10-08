from odoo import fields, models


class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "this model defines property tags"

    name = fields.Char("Tag", required=True)

    _name_uniq = models.Constraint(
        "unique (name)",
        "A property tag name must be unique",
    )
