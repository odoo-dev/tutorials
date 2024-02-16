from odoo import fields, models


class estatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Estate property type model"
    # _rec_name = 'description'
    # to show "description" in dropdown instead of name

    name = fields.Char(required=True, string="Name")
    # description = fields.Char()

    _sql_constraints = [
        ("name_unique", "unique(name)", "The property type must be unique.")
    ]
