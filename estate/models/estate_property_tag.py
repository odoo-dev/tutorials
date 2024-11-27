from odoo import models, fields
from random import randint

class EstatePropertyTag(models.Model):
    _name ="estate.property.tag"
    _description = "Estate property Tag Model"
    _order="name desc"
    _sql_constraints = [('name_uniq', "unique(name)", "The name must be unique.")]
        
    def _default_color(self):
        return randint(1, 11)
    
    name= fields.Char(required=True) 
    color= fields.Integer(default=_default_color)
    