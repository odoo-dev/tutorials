from odoo import models, fields

class EstateProperty(models.Model):
    _name ="estate.property.type"
    _description = "Estate property Type Model"
    _order="id desc"
    _sql_constraints = [('name_uniq', "unique(name)", "The name must be unique.")]
    name= fields.Char(required=True) 
    