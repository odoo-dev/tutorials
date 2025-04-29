from odoo import api, fields, models


class EstatePropertyTypeModel(models.Model):
    _name = "estate_property_type"
    _description = "Real estate property type"
    _order = "sequence"

    _sql_constraints = [
        ("check_type_name", "UNIQUE(name)", "A property type name must be unique.")
    ]

    name = fields.Char(required=True)
    property_ids = fields.One2many("estate_property", "property_type_id")
    sequence = fields.Integer("Sequence", default=1)

    offer_ids = fields.One2many("estate_property_offer", "property_type_id", string="Offers")
    offer_count = fields.Integer(compute="_compute_offer_count")

    @api.depends("offer_ids")
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)