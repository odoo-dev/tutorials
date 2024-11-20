from odoo import fields, models
class EstatePropertyTag(models.Model):
    _name="estate.property.tag"
    _description="estate property tag model"
    _order="name"
    name=fields.Char(required=True)
    _sql_constraints=[('check_name','UNIQUE(name)',
    'The Tag name Must be Unique')]
    color=fields.Integer()

