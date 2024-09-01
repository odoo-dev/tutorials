from odoo import api, fields, models


class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Estate Property Type"
    _sql_constraints = [
        ("unique_property_type_name", "UNIQUE(name)", "A type with this name already exists.")
    ]
    _order = "sequence, name"

    property_ids = fields.One2many("estate.property", "property_type_id")
    offer_ids = fields.One2many("estate.property.offer", "property_type_id")

    name = fields.Char(required=True)
    sequence = fields.Integer(default=1, help="Used to order types. Lower is better.")
    offer_count = fields.Integer(string="Number of Offers", compute="_computer_offer_count")

    @api.depends("offer_ids")
    def _computer_offer_count(self):
        for property_type in self:
            property_type.offer_count = len(property_type.offer_ids)
