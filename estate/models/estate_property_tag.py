from odoo import fields, models
from random import randint

class estatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Estate property tag model"

    name = fields.Char(required=True, string='Name')
    
    def _get_default_color(self):
        return randint(1, 11)

    color = fields.Integer('Color', default=_get_default_color)
