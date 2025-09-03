from odoo import fields, models


class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Property Tag"
    _order = "name"

    name = fields.Char("Property Tag", required=True)
    color = fields.Integer("Color")

    _sql_constraints = [
        ("unique_name", "unique(name)", "The tag name must be unique."),
    ]
