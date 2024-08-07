from odoo import models, fields


class PropertyType(models.Model):
    _name = "real.estate.property.type"
    _description = "Property Type"

    name = fields.Char(string="Property Type", required=True)
    description = fields.Text(string="Description")

    _sql_constraints = [("name", "UNIQUE(name)", "A property type name must be unique")]
