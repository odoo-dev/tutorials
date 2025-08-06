from odoo import fields, models


class EstatePropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Estate Property Tag'
    _sql_constraints = [('name_unique', 'UNIQUE(name)', 'Tag name must be unique!')]
    _order = 'name'

    name = fields.Char(string='Tag Name', required=True)
