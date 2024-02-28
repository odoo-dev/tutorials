# -*- coding: utf-8 -*-

from odoo import models, fields, api, Command
from datetime import timedelta
from odoo.exceptions import ValidationError, UserError

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Offer table for estate property"
    _order = "price desc"

    price = fields.Float(string="Price")
    status = fields.Selection(string="Status", 
        selection=[("accepted", "Accepted"), ("refused", "Refused")], 
        copy=False
    )
    partner_id = fields.Many2one(string="Partner", comodel_name="res.partner", required=True)
    property_id = fields.Many2one(string="Property", comodel_name="estate.property")
    validity = fields.Integer(string="Validity(days)", default=7)
    date_deadline = fields.Date(string="Deadline", compute="_compute_date_deadline", inverse="_inverse_date_deadline", store=True)
    property_type_id = fields.Many2one(related="property_id.property_type_id")

    _sql_constraints = [
        (
            "check_offer_price_positive",
            "CHECK(price > 0)",
            "Expected price must be strictly positive"
        )
    ]


    @api.depends("create_date", "validity")
    def _compute_date_deadline(self):
        for record in self:
            date = record.create_date if record.create_date else fields.Date.today()
            record.date_deadline = date + timedelta(record.validity)
        
    def _inverse_date_deadline(self):
        for record in self:
            record.validity = (record.date_deadline - fields.Date.to_date(record.create_date)).days if record.date_deadline\
                else 0
    
    def action_offer_accept(self):
        self.ensure_one()
        self.status = "accepted"
        self.property_id.write({
            "buyer_id" : self.partner_id,
            "state" : "offer accepted",
            "selling_price" : self.price
        })
        other_offers = self.property_id.offer_ids - self
        other_offers.write({'status' : 'refused'})
            

    def action_offer_refused(self):
        self.ensure_one()
        self.status = "refused"
    
    @api.model_create_multi
    def create(self, vals_list):
        estate_property = self.env['estate.property'].browse(vals_list[0]["property_id"])
        offers = self.search([("property_id", "=", estate_property.id)])
        if len(offers) != 0:
            max_price = estate_property.best_price
            vals_list = list(filter(lambda offer: offer["price"] > max_price, vals_list))
        if estate_property.state != "offer received":
            estate_property.state = "offer received"
        return super().create(vals_list)


    
