from odoo import fields, models


class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Estate Property Type'
    _sql_constraints = [('name_unique', 'UNIQUE(name)', 'Property type name must be unique!')]

    name = fields.Char(string='Type Name', required=True)
