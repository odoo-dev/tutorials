from odoo.exceptions import UserError
from odoo import api, fields, models


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property Offer description test"
    _order = "price desc"

    validity = fields.Integer()
    date_deadline = fields.Date(compute="_compute_validity_date", inverse="_inverse_validity_date")
    price = fields.Float()
    status = fields.Selection([("accepted", "Accepted"), ("refused", "Refused")], copy=False)
    partner_id = fields.Many2one("res.partner", required=True)
    property_id = fields.Many2one("estate.property", required=True)

    _check_price = models.Constraint(
        'CHECK(price > 0)',
        'The offer price must be strictly positive.'
    )

    @api.depends("create_date", "validity")
    def _compute_validity_date(self):
        for offer in self:
            offer.date_deadline = fields.Date.add(offer.create_date, days=offer.validity)

    def _inverse_validity_date(self):
        for offer in self:
            offer.validity = (offer.date_deadline - fields.Date.to_date(offer.create_date)).days

    def action_accept_offer(self):
        for offer in self:

            if offer.property_id.state in ["offer_accepted", "sold"]:
                offer.property_id.buyer_id = offer.partner_id
                offer.property_id.selling_price = offer.price
                offer.property_id.state = "offer_accepted"
                offer.status = "accepted"
            else:
                raise UserError(self.env._("An offer has already been accepted."))

        return True

    def action_refuse_offer(self):
        for offer in self:

            if offer.status == "accepted":
                offer.property_id.selling_price = 0
                offer.property_id.buyer_id = None

            offer.status = "refused"

        return True
