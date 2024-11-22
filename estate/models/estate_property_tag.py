from odoo import models, fields

class EstatePropertyTag(models.Model):
    _name ="estate.property.tag"
    _description = "Estate property Tag Model"
    _order="id desc"
    _sql_constraints = [('name_uniq', "unique(name)", "The name must be unique.")]
    name= fields.Char(required=True) 
    