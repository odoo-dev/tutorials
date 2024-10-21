from odoo import fields, models


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Estate properties types"

    name = fields.Char(string="Name", required=True)
