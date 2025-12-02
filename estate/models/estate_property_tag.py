# 19.0-tutorials-frtan

from odoo import fields, models

class EstatePropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = "Types defined for Estate, example: 'renovated' or 'cozy'. many2many type"
    _order = 'name'
    _name_unique = models.Constraint(
        'unique(name)',
        'Property tag name must be unique'
    )

    name = fields.Char(required=True)
    color = fields.Integer()