# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timedelta

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

    @api.depends("create_date","validity")
    def _compute_date_deadline(self):
        for record in self:
            if record.create_date:
                record.date_deadline = record.create_date + timedelta(days=record.validity)
            else :
                record.date_deadline = fields.Date.today() + timedelta(days=record.validity)
        
    def _inverse_date_deadline(self):
        for record in self:
            if record.date_deadline:
                record.validity = (record.date_deadline - fields.Date.to_date(record.create_date)).days
    
    def offer_accept(self):
        for record in self:
            record.status = "accepted"
            record.property_id.buyer_id = record.partner_id
            record.property_id.state = "sold"
            record.property_id.selling_price = record.price
            other_offers = record.property_id.offer_ids.filtered(lambda offer: offer.id != record.id)
            other_offers.write({'status': 'refused'})
            

    def offer_refused(self):
        for record in self:
            record.status = "refused"
    
    _sql_constraints = [
        (
            "check_offer_price_positive",
            "CHECK(price > 0)",
            "Expected price must be strictly positive"
        )
     ]