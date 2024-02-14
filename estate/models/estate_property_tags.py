from odoo import fields, models

class EstatePropertyTags(models.Model):
    _name = "estate.property.tags"
    _description = "Model for Real Estate Property Tags"

    name = fields.Char(string = "Name" , required=True)

    #SQL constraints
    _sql_constraints = [
        ('uniq_name', 'unique(name)', 'A property tag name must be unique.'),
    ]
