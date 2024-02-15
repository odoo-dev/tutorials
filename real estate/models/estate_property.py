# -*- coding: utf-8 -*-

from odoo import models, fields
from datetime import timedelta

class estate_property(models.Model):
    _name = "estate.property"
    _description = "estate property table for real estate"

    name = fields.Char(string="Name", required=True)
    description = fields.Text(string="Description", default="When duplicated status and date are not copied")
    postcode = fields.Char(string="Postcode", default="ABCD")
    date_availability = fields.Date(string="Available From", default=lambda self: fields.Date.today()+timedelta(days=3*30), copy=False)
    expected_price = fields.Float(string="Expected Price", default=0.0, required=True)
    selling_price = fields.Float(string="Selling Price", default=0.0, readonly=True, copy=False)
    bedrooms = fields.Integer(string="Bedrooms", default=2)
    living_area = fields.Integer(string="Living Area", default=0)
    facades = fields.Integer(string="Facades", default=0)
    garage = fields.Boolean(string="Garage", default=False)
    garden = fields.Boolean(string="Garden", default=False)
    garden_area = fields.Integer(string="Garden Area", default=0)
    garden_orientation = fields.Selection(string="Garden Orientation", 
        selection=[("n", "North"), ("s", "South"), ("w", "West"), ("e", "East")]
    )
    active =  fields.Boolean(string="Active")
    state = fields.Selection(string="State", 
        selection=[("new", "New"), ("offer received", "Offer Recieved"), ("offer accepted", "Offer Accepted"), ("sold", "Sold"), ("canceled", "Canceled")]
    )
    buyer_id = fields.Many2one(string="Buyer", comodel_name="res.partner")
    salesperson_id = fields.Many2one(string="Salesperson", comodel_name="res.users", default=lambda self:self.env.user.id)
    tag_ids = fields.Many2many(string ="Tags", comodel_name="estate.property.tag")
    offer_ids = fields.One2many(string="Offers", comodel_name="estate.property.offer", inverse_name="property_id")

