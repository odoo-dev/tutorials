from odoo import models, fields, api


class EstatePropertyType(models.Model):
    # Private attributes
    _name = "estate.property.type"
    _description = "Type of estate property"
    _order = "sequence, name"

    # Field declarations
    name = fields.Char(required=True)
    sequence = fields.Integer(
        "Sequence", default=1, help="Used to order types. Lower is better."
    )
    property_ids = fields.One2many("estate.property", "property_type_id")
    offer_ids = fields.One2many("estate.property.offer", "property_type_id")
    offer_count = fields.Char(compute="_compute_offers_count")

    # SQL constraints and indexes
    _unique_name = models.UniqueIndex(
        "(name)", "Type with the same name already exists."
    )

    # Compute, inverse and search methods
    @api.depends("offer_ids")
    def _compute_offers_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)
