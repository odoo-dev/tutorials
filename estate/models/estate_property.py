# -*- coding: utf-8 -*-
# licence

from odoo import api
from odoo import fields
from odoo import models
from odoo.exceptions import UserError


class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = "Estate property"

    name = fields.Char("Title", required=True, translate=True)
    description = fields.Text("Property description")
    postcode = fields.Char("Postcode")
    date_availability = fields.Date("Date of availability", default=lambda _self: fields.Date.add(fields.Date.today(), days=30), copy=False)
    expected_price = fields.Float("Expected price", required=True)
    selling_price = fields.Float("Selling price", readonly=True, copy=False)
    bedrooms = fields.Integer("No. of bedrooms", default=2)
    living_area = fields.Integer("Living area (sqm)")
    facades = fields.Integer("No. of facades")
    garage = fields.Boolean("Has a garage")
    garden = fields.Boolean("Has a garden", default=False)
    garden_area = fields.Integer("Garden area (sqm)", default=0)
    garden_orientation = fields.Selection(
        string="Garden orientation",
        selection=[
            ('north', "North"),
            ('south', "South"),
            ('east', "East"),
            ('west', "West")
            ],
        default=None,
        )
    # Reserved
    active = fields.Boolean("Active", default=True)
    state = fields.Selection(
        string="Status",
        selection=[
            ('new', "New"),
            ('recieved', "Offer Received"),
            ('accepted', "Offer Accepted"),
            ('sold', "Sold"),
            ('cancelled', "Cancelled")
            ],
        required=True,
        copy=False,
        default='new',
        )
    # Relational
    property_type_id = fields.Many2one('estate.property.type', string="Type")
    tag_ids = fields.Many2many('estate.property.tag', string="Tags")
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string="Offers")
    buyer_id = fields.Many2one('res.partner', string="Buyer")
    salesperson_id = fields.Many2one('res.users', string="Salesperson", default=lambda self: self.env.user)
    # Computed
    area_total = fields.Float("Total area", compute='_compute_area_total')
    best_offer = fields.Float("Best offer", compute='_compute_best_offer')

    def _compute_area_total(self):
        for record in self:
            record.area_total = record.living_area + record.garden_area

    @api.depends('offer_ids.price')
    def _compute_best_offer(self):
        for record in self:
            best = 0
            for offer in record.offer_ids:
                if offer.price > best:
                    best = offer.price
            record.best_offer = best

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = None

    def action_set_sold(self):
        for record in self:
            if record.state != 'cancelled':
                record.state = 'sold'
            else:
                raise UserError("The property is already cancelled.")
        return True

    def action_set_cancelled(self):
        for record in self:
            if record.state != 'sold':
                record.state = 'cancelled'
            else:
                raise UserError("The property is already sold.")
        return True
