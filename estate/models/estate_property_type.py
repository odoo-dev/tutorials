from odoo import fields, models, api

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Model for Real Estate Property Types"
    _order = "name"

    name = fields.Char(string = "Name" , required=True)
    property_ids = fields.One2many("estate.property", "property_type_id")
    sequence = fields.Integer('Sequence', default=1)
    offer_ids = fields.One2many("estate.property.offer", "property_type_id")
    offer_count = fields.Integer(string="Offer count", compute="_compute_offer")

    #SQL constraints
    _sql_constraints = [
        ('uniq_name', 'unique(name)', 'A property type name must be unique.'),
    ]

    #computed method
    @api.depends("offer_ids")
    def _compute_offer(self):
        for record in self:
            record.offer_count = len(record.offer_ids)
