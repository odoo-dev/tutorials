from odoo import fields, models

class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = """
    Tags to attach to properties
    """

    name = fields.Char(required=True)