from odoo import fields, models


class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = "Estate property types"
    _order = 'sequence, name'

    name = fields.Char(required=True)
    sequence = fields.Integer('Sequence', default=1, help="Used to order types.")
    property_ids = fields.One2many('estate.property', 'property_type_id', string="Properties", copy=False)
    offer_ids = fields.One2many(related='property_ids.offer_ids')
    offer_count = fields.Integer(compute='_compute_offer_count')

    _unique_name = models.Constraint(
        'UNIQUE(name)',
        'Each property type should have a unique name.'
    )

    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)
