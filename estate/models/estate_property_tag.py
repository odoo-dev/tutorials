from odoo import models, fields

class EstatePropertyTag(models.Model):
    _name ="estate.property.tag"
    _description = "Estate property Tag Model"
    _order="name desc"
    _sql_constraints = [('name_uniq', "unique(name)", "The name must be unique.")]
    name= fields.Char(required=True) 
    color= fields.Integer()
    