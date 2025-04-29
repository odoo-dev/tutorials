from odoo import fields, models


class EstatePropertyTagModel(models.Model):
    _name = "estate_property_tag"
    _description = "Estate property tag"
    _order = "name"

    _sql_constraints = [
        ("check_tag_name", "UNIQUE(name)", "A property tag name must be unique.")
    ]

    name = fields.Char(required=True)
    color = fields.Integer()