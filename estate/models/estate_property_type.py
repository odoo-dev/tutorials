from odoo import api, fields, models

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = """
    The type of the estate. Can be either 'house' or 'apartment'
    """
    _sql_constraints = [
        ('check_property_type', 'UNIQUE(name)', 'The name must be unique.')
    ]
    _order = "sequence, name"

    name = fields.Char(required=True)
    property_ids = fields.One2many("estate.property", "property_type_id")
    offer_ids = fields.One2many("estate.property.offer", "property_type_id")
    offer_count = fields.Integer(compute='_compute_offers', string="Offers", copy=False, readonly=True)
    sequence = fields.Integer('Sequence')

    @api.depends("offer_ids")
    def _compute_offers(self):
        for record in self:
            record.offer_count = len(record.offer_ids)