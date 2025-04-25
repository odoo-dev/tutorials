from odoo import fields, models


class EstatePropertyTagModel(models.Model):
    _name = "estate_property_tag"
    _description = "Estate property tag"

    name = fields.Char(required=True)