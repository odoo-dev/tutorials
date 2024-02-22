# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timedelta
from odoo.exceptions import ValidationError, UserError

class estate_property_offer(models.Model):
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

    @api.depends("create_date","validity")
    def _compute_date_deadline(self):
        for record in self:
            if record.create_date:
                record.date_deadline = record.create_date + timedelta(days=record.validity)
            else:
                record.date_deadline = fields.Date.today() + timedelta(days=record.validity)
        
    def _inverse_date_deadline(self):
        for record in self:
            if record.date_deadline:
                record.validity = (record.date_deadline - fields.Date.to_date(record.create_date)).days
    
    def action_offer_accept(self):
        self.ensure_one()
        self.status = "accepted"
        self.property_id.buyer_id = self.partner_id
        self.property_id.state = "offer accepted"
        self.property_id.selling_price = self.price
        other_offers = self.property_id.offer_ids - self
        other_offers.write({'status': 'refused'})
            

    def action_offer_refused(self):
        self.status = "refused"
    
    @api.model_create_multi
    def create(self, vals):
        other_offers = self.search([("property_id", "=", vals[0]["property_id"])])
        if len(other_offers) != 0:
            max_price = other_offers[0].property_id.best_price
            for offer in vals:
                if offer["price"] < max_price:
                    vals.remove(offer)
        return super().create(vals)


    
