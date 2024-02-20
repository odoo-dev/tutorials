# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timedelta

class estate_property_offer(models.Model):
    _name="estate.property.offer"
    _description="Offer table for estate property"

    price = fields.Float(string="Price")
    status = fields.Selection(string="Status", 
        selection=[("accepted", "Accepted"), ("refused", "Refused")], 
        copy=False
    )
    partner_id = fields.Many2one(string="Partner", comodel_name="res.partner", required=True)
    property_id = fields.Many2one(string="Property", comodel_name="estate.property")
    validity = fields.Integer(string="Validity(days)", default=7)
    date_deadline = fields.Date(string="Deadline", compute="_compute_date_deadline", inverse="_inverse_date_deadline", store=True)

    @api.depends("create_date","validity")
    def _compute_date_deadline(self):
        if self.create_date:
            self.date_deadline = self.create_date + timedelta(days=self.validity)
        else :
            self.date_deadline = fields.Date.today() + timedelta(days=self.validity)
    
    def _inverse_date_deadline(self):
            if self.date_deadline:
                self.validity = (self.date_deadline - fields.Date.to_date(self.create_date)).days
    
    def offer_accept(self):
        for record in self:
            record.status = "accepted"
            record.property_id.buyer_id = record.partner_id
            record.property_id.state = "sold"
            record.property_id.selling_price = record.price
            other_offers = record.property_id.offer_ids.filtered(lambda offer: offer.id != self.id)
            other_offers.status = "refused"
            

    def offer_refused(self):
        self.status = "refused"
    