# -*- coding: utf-8 -*-

from odoo import fields, models

class Estate_Property(models.Model):
    _name = "estate_property"
    _description = "Estate properties"

    name = fields.Char(required = True)
    description = fields.Text()
    postcode = fields.Char(help = 'Une adresse serait mieux mais bon...')
    date_availability = fields.Date()
    expected_price = fields.Float(required = True)
    selling_price = fields.Float()
    bedrooms = fields.Integer()
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection([('north', 'North'), ('south', 'South'), ('west', 'West'), ('east', 'East')])