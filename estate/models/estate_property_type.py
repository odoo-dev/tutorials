from odoo import api, fields, models


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Real Estate Property Type"
    _order = "sequence, name"

    name = fields.Char("Property Type", required=True)
    property_ids = fields.One2many(
        "estate.property", "property_type_id", string="Properties"
    )
    sequence = fields.Integer("Sequence")
    offer_ids = fields.One2many(
        "estate.property.offer", "property_type_id", string="Offers"
    )
    offer_count = fields.Integer("Offer Count", compute="_compute_offer_count")

    _sql_constraints = [
        ("unique_name", "unique(name)", "The property type name must be unique."),
    ]

    @api.depends("offer_ids")
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)
