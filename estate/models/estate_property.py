# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero


class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'Estate Property'
    _order = 'id desc'
    _sql_constraints = [
        ('positive_expected_price', 'check (expected_price > 0)', 'The expected price must be strictly positive.'),
        ('positive_selling_price', 'check (selling_price > 0)', 'The selling price must be positive.'),
    ]

    name = fields.Char(required=True, string="Title")
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(
        default=fields.Date.add(fields.Date.today(), months=3), copy=False, string="Available From")
    # Price
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    best_price = fields.Float(compute='_compute_best_price', string="Best Offer")
    # Area
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer(string="Living Area (sqm)")
    facades = fields.Integer()
    garage = fields.Char()
    garden = fields.Boolean()
    garden_area = fields.Integer(string="Garden Area (sqm)")
    garden_orientation = fields.Selection(
        selection=[('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')], )
    total_area = fields.Integer(compute='_compute_total_area')

    property_type_id = fields.Many2one(
        comodel_name='estate.property.type',
        string="Property Type")
    buyer_id = fields.Many2one(
        comodel_name='res.partner',
        string="Buyer",
        copy=False)
    salesperson_id = fields.Many2one(
        comodel_name='res.users',
        string="Salesman",
        default=lambda self: self.env.user)
    offer_ids = fields.One2many(
        comodel_name='estate.property.offer',
        inverse_name='property_id',
        string="Offers")
    tag_ids = fields.Many2many(
        comodel_name='estate.property.tag',
        string='Tags')

    active = fields.Boolean(default=True)
    state = fields.Selection(
        selection=[
            ('new', 'New'),
            ('offer_received', 'Offer Received'),
            ('offer_accepted', 'Offer Accepted'),
            ('sold', 'Sold'),
            ('cancelled', 'Cancelled')
        ],
        required=True,
        default='new', )

    @api.depends('offer_ids.price')
    def _compute_best_price(self):
        for record in self:
            if record.offer_ids:
                record.best_price = max(record.offer_ids.mapped('price'))
            else:
                record.best_price = 0

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.constrains('selling_price', 'expected_price')
    def _check_selling_price(self):
        for record in self:
            selling_price_zero = float_is_zero(record.selling_price, precision_digits=2)
            selling_price_constraint = float_compare(record.selling_price, record.expected_price * 0.9,
                                                     precision_digits=2) == -1
            if not selling_price_zero and selling_price_constraint:
                raise ValidationError(
                    "The selling price must be at least 90% of the expected price! You must reduce the expected price if you want to accept this offer.")

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = ''

    @api.ondelete(at_uninstall=False)
    def _unlink_if_state_new_or_cancelled(self):
        if any(record.state not in ['new', 'cancelled'] for record in self):
            raise UserError("Can't delete property")

    def action_set_sold(self):
        for record in self:
            if record.state == 'cancelled':
                raise UserError("Cancelled properties cannot be sold")
            elif record.state != 'offer_accepted':
                raise UserError("Accept offer to sell property")
            record.state = 'sold'
        return True

    def action_set_cancel(self):
        for record in self:
            if record.state == 'sold':
                raise UserError("Sold properties cannot be cancelled")
            record.state = 'cancelled'
        return True
