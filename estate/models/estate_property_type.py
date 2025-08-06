from odoo import fields, models, api


class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Estate Property Type'
    _sql_constraints = [('name_unique', 'UNIQUE(name)', 'Property type name must be unique!')]
    _order = 'name'

    name = fields.Char(string='Type Name', required=True)
    property_ids = fields.One2many(comodel_name='estate.property', inverse_name='property_type_id', string='Properties')
    sequence = fields.Integer(string='Sequence', required=True, default=1)
    offer_ids = fields.One2many(comodel_name='estate.property.offer', inverse_name='property_type_id', string='Offers')
    offer_count = fields.Integer(string='Offer Count', compute='_compute_offer_count', readonly=True)

    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)
