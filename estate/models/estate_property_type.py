# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class PropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Estate property type info"

    name = fields.Char(required=True)

    property_ids = fields.One2many("estate.property", "property_type_id")

    _unique_name = models.Constraint(
        "UNIQUE(name)",
    )
