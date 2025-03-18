from odoo import models, fields

class PropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Real Estate Property Tag"

    name = fields.Char(required=True)
    _sql_constraints = [
        ("name_unique", "UNIQUE(name)", "The property tag name must be unique.")
    ]