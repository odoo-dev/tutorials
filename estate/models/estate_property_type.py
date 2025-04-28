from odoo import fields, models


class EstatePropertyTypeModel(models.Model):
    _name = "estate_property_type"
    _description = "Real estate property type"

    _sql_constraints = [
        ("check_type_name", "UNIQUE(name)", "A property type name must be unique.")
    ]

    name = fields.Char(required=True)