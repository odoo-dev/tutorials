from odoo import fields, models

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = """
    The type of the estate. Can be either 'house' or 'apartment'
    """
    _sql_constraints = [
        ('check_property_type', 'UNIQUE(name)', 'The name must be unique.')
    ]
    _order = "sequence, name"

    name = fields.Char(required=True)
    property_ids = fields.One2many("estate.property", "property_type_id")
    sequence = fields.Integer('Sequence')