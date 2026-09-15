from odoo import api, fields, models


class PropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Estate Property Type"
    _order = "name"

    _check_unique_name = models.Constraint(
        "UNIQUE (name)",
        "The name must be unique",
    )

    name = fields.Char(required=True)
    property_ids = fields.One2many("estate.property", "property_type_id", "Property")
    offers_ids = fields.One2many("estate.property.offer", "property_type_id")
    offer_count = fields.Integer(compute="_compute_offers_count")
    sequence = fields.Integer(default=1, help="Used to order type. Lower is better.")

    @api.depends("offers_ids")
    def _compute_offers_count(self):
        for record in self:
            record.offer_count = len(record.offers_ids)
