from odoo import fields, models


class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Estate Property Tag"
    _sql_constraints = [
        ("unique_property_tag_name", "UNIQUE(name)", "A tag with this name already exists.")
    ]
    _order = "name"

    name = fields.Char(required=True)
    color = fields.Integer()
