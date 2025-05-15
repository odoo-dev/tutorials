from odoo import api, fields, models
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta


class EstatePropertyOfferModel(models.Model):
    _name = "estate_property_offer"
    _description = "Estate property offer"
    _order = "price desc"

    _sql_constraints = [
        ("check_offer_price", "CHECK(price > 0)", "An offer price must be strictly positive"),
    ]

    price = fields.Float()
    status = fields.Selection([("accepted", "Accepted"), ("refused", "Refused")], copy=False)
    partner_id = fields.Many2one("res.partner", required=True)
    property_id = fields.Many2one("estate_property", required=True)

    validity = fields.Integer(default=7)
    create_date = fields.Date(default=fields.Date.today())
    date_deadline = fields.Date(compute="_compute_deadline", inverse="_inverse_deadline")

    property_type_id = fields.Many2one(related="property_id.property_type_id", store=True)

    @api.depends("validity")
    def _compute_deadline(self):
        for record in self:
            record.date_deadline = record.create_date + relativedelta(days=record.validity)

    def _inverse_deadline(self):
        for record in self:
            record.validity = (self.date_deadline - fields.Date.today()).days

    def action_accept(self):
        for record in self:
            offers = record.property_id.offer_ids
            for offer in offers:
                if offer != record and offer.status == "accepted":
                    raise UserError("Only one offer can be accepted for a property")

            record.status = "accepted"
            record.property_id.selling_price = record.price
            record.property_id.buyer_id = record.partner_id
            record.property_id.state = "offer_accepted"

        return True
    
    def action_refuse(self):
        for record in self:
            record.status = "refused"

        return True

    @api.model
    def create(self, vals):
        property_id = self.env["estate_property"].browse(vals["property_id"])
        if property_id.state == "sold":
            raise UserError("New offer cannot be made to a sold property.")
        if vals["price"] < property_id.best_price:
            raise UserError("New offer cannot have price lower than the price of existing offer.")
        
        property_id.state = "offer_received"

        return super().create(vals)