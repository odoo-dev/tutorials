from odoo import models, fields

class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Type of a property'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')

class EstatePropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Type of a property'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')