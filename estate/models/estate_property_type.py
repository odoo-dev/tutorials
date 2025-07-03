from odoo import fields, models

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = """
    The type of the estate. Can be either 'house' or 'apartment'
    """

    name = fields.Char(required=True)