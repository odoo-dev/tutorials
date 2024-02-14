from odoo import fields, models, api
from datetime import datetime, timedelta

class EstatePropertyTags(models.Model):
    _name = "estate.property.offer"
    _description = "Model for Real Estate Property Offers"

    price = fields.Float(string = "Price")
    status = fields.Selection([('accepted', 'Accepted'),('refused', 'Refused')], string='Status',copy=False)
    partner_id = fields.Many2one("res.partner", string="Partner", required=True)
    property_id = fields.Many2one("estate.property", string="Property", required=True)
    validity = fields.Integer(string="Validity(days)", default=7)
    date_deadline = fields.Date(string="Deadline", compute="_compute_date_deadline", inverse="_inverse_date_deadline")

    #compute method
    @api.depends("create_date","validity")
    def _compute_date_deadline(self):
        for offer in self:
            if offer.create_date:
                offer.date_deadline = offer.create_date + timedelta(days=offer.validity)
            else:
                offer.date_deadline = datetime.now() + timedelta(days=offer.validity)

    #inverse method
    def _inverse_date_deadline(self):
        for offer in self:
            offer.validity = (offer.date_deadline - (offer.create_date).date()).days
