from odoo import fields, models


class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Estate property tag description"

    name = fields.Char(required=True)

    _unique_tag_name = models.Constraint(
        'UNIQUE(name)',
        'The property tag name must be unique'
    )
