from odoo import fields, models

class EstatePropertyTags(models.Model):
    _name = "estate.property.tags"
    _description = "Model for Real Estate Property Tags"
    _order = "name"

    name = fields.Char(string = "Name" , required=True)
    color = fields.Integer('Color')

    #SQL constraints
    _sql_constraints = [
        ('uniq_name', 'unique(name)', 'A property tag name must be unique.'),
    ]
