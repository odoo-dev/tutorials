# -*- coding: utf-8 -*-

from odoo import models, fields

class estate_property(models.Model):
    _name = "estate.property"
    _description = "estate property table for real estate"

    name = fields.Char(string="Name", default="Property name", required=True)
    description = fields.Text(string="Description", default="some desc")
    postcode = fields.Char(string="Postcode", default="ABCD")
    date_availability = fields.Date(string="Date Availability")
    expected_price = fields.Float(string="Expected Price", default=0.0, required=True)
    selling_price = fields.Float(string="Selling Price", defaultcd=0.0)
    bedrooms = fields.Integer(string="Bedrooms", default=0)
    living_area = fields.Integer(string="Living Area", default=0)
    facades = fields.Integer(string="Facades", default=0)
    garage = fields.Boolean(string="Garage", default=False)
    garden = fields.Boolean(string="Garden", default=False)
    garden_area = fields.Integer(string="Garden Area", default=0)
    garden_orientation = fields.Selection(string="Garden Orientation", selection=[("n", "North"),("s", "South"),("w", "West"),("e", "East")])