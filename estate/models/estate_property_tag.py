from odoo import fields, models


class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Estate Property Tag"

    name = fields.Char(required=True)

    _check_unique_tag = models.Constraint(
        'UNIQUE(name)',
        'A tag with that name already exists.'
    )
