from odoo import fields, models


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Contains the different types of properties"
    _check_name_is_unique = models.Constraint('UNIQUE(name)')

    name = fields.Char(required=True)
