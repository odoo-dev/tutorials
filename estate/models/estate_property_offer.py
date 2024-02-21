from odoo import fields, models, api
from datetime import datetime, timedelta
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Model for Real Estate Property Offers"
    _order = "price desc"

    price = fields.Float(string = "Price")
    status = fields.Selection([('accepted', 'Accepted'),('refused', 'Refused')], string='Status',copy=False)
    partner_id = fields.Many2one("res.partner", string="Partner", required=True)
    property_id = fields.Many2one("estate.property", string="Property", required=True)
    validity = fields.Integer(string="Validity(days)", default=7)
    date_deadline = fields.Date(string="Deadline", compute="_compute_date_deadline", inverse="_inverse_date_deadline")
    property_type_id = fields.Many2one("estate.property.type", string="Property type", related="property_id.property_type_id", store=True)

    #SQL constraints
    _sql_constraints = [
        ("check_offer_price", "CHECK(price > 0)", "The offer price must be strictly positive")
    ]

    #compute method
    @api.depends("create_date","validity")
    def _compute_date_deadline(self):
        for record in self:
            if record.create_date:
                record.date_deadline = record.create_date + timedelta(days=record.validity)
            else:
                record.date_deadline = datetime.now() + timedelta(days=record.validity)

    #inverse method
    def _inverse_date_deadline(self):
        for record in self:
            record.validity = (record.date_deadline - (record.create_date).date()).days

    #crud methods
    @api.model
    def create(self, vals):
        prop = self.env["estate.property"].browse(vals['property_id'])
        if prop.offer_ids:
            max_offer = max(prop.offer_ids.mapped("price"))
            if float_compare(vals.get("price"), max_offer, precision_rounding=0.01) < 0:
                raise UserError("The offer must be higher than %.2f" % max_offer)
        prop.state = 'offer_received'
        return super().create(vals)

    #buttons
    def accept_offer(self):
        for record in self:
            if record.property_id.buyer_id:
                raise UserError("You can not accept more than 1 offer")
            else:
                record.status = 'accepted'
                record.property_id.state = 'offer_accepted'
                record.property_id.buyer_id = record.partner_id
                record.property_id.selling_price = record.price
    
    def refuse_offer(self):
        for record in self:
            record.status = 'refused'
            if record.property_id.buyer_id == record.partner_id and record.property_id.selling_price == record.price:
                record.property_id.buyer_id = False
                record.property_id.selling_price = 0
