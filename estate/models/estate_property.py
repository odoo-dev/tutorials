# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models
from dateutil.relativedelta import relativedelta


class Property(models.Model):
    _name = "estate_property"
    _description = "Estate Property"

    name = fields.Char(
        "Title",
        required=True
    )
    active = fields.Boolean(default=True)
    description = fields.Text()
    postcode = fields.Char("Postcode")
    date_availability = fields.Date(
        "Available From",
        copy=False, 
        default=lambda self: fields.Date.today() + relativedelta(months=3)
    )
    expected_price = fields.Float(
        "Expected Price",
        required=True,
    )
    selling_price = fields.Float(
        "Selling Price",
        readonly=True,
        copy=False
    )
    bedrooms = fields.Integer(
        "Bedrooms",
        default=2,
    )
    living_area = fields.Integer("Living Area (sqm)")
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        string='Garden Orientation',
        selection=[
            ('north', 'North'), 
            ('south', 'South'), 
            ('east', 'East'), 
            ('west', 'West'),
        ],
    )
    state = fields.Selection(
        string='State',
        selection=[
            ('new', "New"),
            ('offer_received', "Offer Received"),
            ('offer_accepted', "Offer Accepted"),
            ('sold', "Sold"),
            ('canceled', "Canceled"),
        ],
        required=True,
        copy=False,
        default='new',
    )