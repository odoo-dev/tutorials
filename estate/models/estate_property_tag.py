from odoo import fields,models

class EstatePropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'real estate property tag'

    name= fields.Char(required=True)
