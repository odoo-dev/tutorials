# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_is_zero, float_compare

class EstateProperty(models.Model):
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
    property_img = fields.Image(string="Property Image")

    _sql_constraints = [
        (
            "check_expected_price_positive",
            "CHECK(expected_price >= 0)",
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
        for record in self:
            record.best_price = max(record.offer_ids.mapped("price")) if len(record.offer_ids.mapped("price")) > 0 \
                else 0 
            
    @api.depends("living_area","garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.constrains("selling_price")
    def _check_selling_price(self):
        for record in self:
            if not float_is_zero(record.selling_price,2) and float_compare(record.selling_price,record.expected_price*0.9,2) == -1:
                raise ValidationError("Selling price must be greater than 90% of expected price")

    @api.onchange("garden")
    def _onchange_garden(self):
        self.ensure_one()
        area, orientation = (10, "n") if self.garden else (0, "")
        self.write({
            "garden_area" : area,
            "garden_orientation" : orientation,
        })
    
    @api.ondelete(at_uninstall=False)
    def _unlink_check_state(self):
        for record in self:
            if record.state not in ("new", "canceled"):
                raise UserError("Cannot delete a record that is neither new nor canceled")

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
