from odoo import fields, models

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Model for Real Estate Property Types"

    name = fields.Char(string = "Name" , required=True)

    #SQL constraints
    _sql_constraints = [
        ('uniq_name', 'unique(name)', 'A property type name must be unique.'),
    ]
