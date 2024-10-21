# -*- coding: utf-8 -*-
from odoo import fields, models
from dateutil.relativedelta import relativedelta

def format(l: list):
    return [(field, field.title()) for field in l]

class EstateProperty(models.Model):

    _name = 'estate.property'
    _description = 'Estate Property modelisation'

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(default=lambda x: fields.Date.today() + relativedelta(months=3), copy=False)
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(string='Orientation',
                                          selection=format(['north', 'south', 'east', 'west']))
    active = fields.Boolean(default=True)
    state = fields.Selection(string='State',
                             selection=format(['new', 'offer received', 'offer accepted', 'sold', 'cancelled']),
                             default='new')