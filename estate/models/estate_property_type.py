from odoo import api,fields, models


class estatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Estate property type model"
    _order = "sequence, name"

    # _rec_name = 'description'
    # to show "description" in dropdown instead of name

    name = fields.Char(required=True, string="Name")
    sequence = fields.Integer(string='Sequence')
    # description = fields.Char()
    property_ids = fields.One2many("estate.property", "property_type_id", string=" ")
    offer_ids = fields.One2many("estate.property.offer", "property_type_id")
    offer_count = fields.Integer(compute="_compute_offer_count", string="Total Offers")
    
    @api.depends("offer_ids")
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)

    _sql_constraints = [
        ("name_unique", "unique(name)", "The property type must be unique.")
    ]
       