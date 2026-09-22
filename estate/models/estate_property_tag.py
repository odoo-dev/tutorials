from odoo import fields, models


class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Estate Property Type"
    _order = "name"

    name = fields.Char()
    color = fields.Integer()
    _unique_name = models.Constraint(
        'unique (name)',
        "Tag nmust be unique!",
    )
