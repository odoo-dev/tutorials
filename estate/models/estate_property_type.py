# -*- coding: utf-8 -*-

from odoo import api, fields, models


class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Property Type'
    _order = 'sequence asc, name asc'
    _sql_constraints = [
        ('unique_name', 'unique (name)', 'The name must be unique.'),
    ]

    name = fields.Char(required=True, string="Type")
    sequence = fields.Integer(default=1, help="Used to order stages. Lower is better.")
    offer_count = fields.Integer(compute='_compute_offer_count')

    property_ids = fields.One2many(
        comodel_name='estate.property',
        inverse_name='property_type_id',
        string="Properties")
    offer_ids = fields.One2many(
        comodel_name='estate.property.offer',
        inverse_name='property_type_id',
        string="Offers")

    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids or [])
