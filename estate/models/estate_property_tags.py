from odoo import fields, models


class EstatePropertyTags(models.Model):
    _name = "estate.property.tags"
    _description = "Estate properties tags"

    name = fields.Char(string="Name", required=True)
