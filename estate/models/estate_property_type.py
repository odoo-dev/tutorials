from odoo import api, fields, models


class EstatePropertyType(models.Model):
    ## Private attributes ##
    _name = "estate.property.type"
    _description = "Real estate property types"
    _order = "sequence, name"

    ## Fields declaration ##
    sequence = fields.Integer(default=1)
    name = fields.Char(required=True)
    property_ids = fields.One2many("estate.property", inverse_name="property_type_id")
    offer_ids = fields.One2many(
        "estate.property.offer",
        inverse_name="property_type_id",
    )
    offer_count = fields.Integer(compute="_compute_offer_count")

    ## Compute methods ##
    @api.depends("offer_ids")
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)
