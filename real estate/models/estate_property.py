# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_is_zero, float_compare

class estate_property(models.Model):
    _name = "estate.property"
    _description = "estate property table for real estate"
    _order = "id desc"

    name = fields.Char(string="Name", required=True)
    description = fields.Text(string="Description", default="When duplicated status and date are not copied")
    postcode = fields.Char(string="Postcode", default="ABCD")
    date_availability = fields.Date(string="Available From", default=lambda self: fields.Date.today()+timedelta(days=3*30), copy=False)
    expected_price = fields.Float(string="Expected Price", required=True)
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
    active =  fields.Boolean(string="Active", default=True)
    state = fields.Selection(string="State", 
        selection=[("new", "New"), ("offer received", "Offer Recieved"), ("offer accepted", "Offer Accepted"), ("sold", "Sold"), ("canceled", "Canceled")],
        default="new"
    )
    buyer_id = fields.Many2one(string="Buyer", comodel_name="res.partner")
    salesperson_id = fields.Many2one(string="Salesperson", comodel_name="res.users", default=lambda self:self.env.user.id)
    tag_ids = fields.Many2many(string ="Tags", comodel_name="estate.property.tag")
    offer_ids = fields.One2many(string="Offers", comodel_name="estate.property.offer", inverse_name="property_id")
    total_area = fields.Integer(string="Total area(sqm)", compute="_compute_total_area")
    best_price = fields.Integer(string="Best price", compute="_compute_best_price")
    property_type_id = fields.Many2one(string="Property Type", comodel_name="estate.property.type")

    _sql_constraints = [
        (
            "check_expected_price_positive",
            "CHECK(expected_price > 0)",
            "Expected price must be strictly positive"
        ),
        (
            "check_selling_price_positive",
            "CHECK(selling_price >= 0)",
            "Selling price must be positive"
        )
    ]
    
    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        self.ensure_one()
        if len(self.offer_ids.mapped('price'))>0:
            self.best_price = max(self.offer_ids.mapped('price'))
        else:
            self.best_price = 0
    
    def action_property_cancel(self):
        self.ensure_one()
        if self.state != "sold":
            self.state = "canceled"
        else:
            raise UserError("Sold properties cannot be canceled")
    
    def action_property_sold(self):
        self.ensure_one()
        if self.state != "canceled":
            self.state = "sold"
        else:
            raise UserError("Canceled properties can not be sold")
            
    @api.depends("living_area","garden_area")
    def _compute_total_area(self):
        self.total_area = self.living_area + self.garden_area

    @api.onchange("garden")
    def _onchange_garden(self):
        self.ensure_one()
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "n"
        else:
            self.garden_area = 0
            self.garden_orientation = ""

    @api.constrains('selling_price')
    def _check_selling_price(self):
        self.ensure_one()
        if not float_is_zero(self.selling_price,2) and float_compare(self.selling_price,self.expected_price*0.9,2) == -1:
            raise ValidationError("Selling price must be greater than 90% of expected price")

    @api.ondelete(at_uninstall=False)
    def _check_state(self):
        for record in self:
            if record.state not in ("new", "canceled"):
                raise ValidationError("Cannot delete a record that is neither new nor canceled")
        