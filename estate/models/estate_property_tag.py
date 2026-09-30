from odoo import fields, models


class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "this model defines property tags"

    name = fields.Char("Tag", required=True)
