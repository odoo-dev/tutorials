from odoo import fields, models

class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = """
    Tags to attach to properties
    """
    _sql_constraints = [
        ('check_tags', 'UNIQUE(name)', 'The name must be unique.')
    ]
    _order = "name"


    name = fields.Char(required=True)
    color = fields.Integer()