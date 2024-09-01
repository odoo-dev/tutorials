from odoo import _, api, fields, models
from odoo.exceptions import UserError


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property Offer"
    _sql_constraints = [
        ("nonnegative_property_offer_price", "CHECK(price >= 0)", "The offer price of a property can't be negative."),
    ]
    _order = "price desc"

    partner_id = fields.Many2one("res.partner", string="Partner", required=True)
    property_id = fields.Many2one("estate.property", required=True)
    property_type_id = fields.Many2one(string="Property Type", related="property_id.property_type_id", store=True)

    price = fields.Float(string="Price")
    status = fields.Selection(
        string="Offer Status",
        copy=False,
        selection=[
            ("accepted", "Accepted"),
            ("refused", "Refused"),
        ],
    )

    validity = fields.Integer(string="Validity (days)", required=True, default=7)
    date_deadline = fields.Date(string="Offer deadline", compute="_compute_date_deadline", inverse="_inverse_date_deadline")

    @api.depends("validity")
    def _compute_date_deadline(self):
        for offer in self:
            if offer.create_date:
                offer.date_deadline = fields.Datetime.add(offer.create_date, days=offer.validity)
            else:
                offer.date_deadline = fields.Datetime.add(fields.Datetime.today(), days=offer.validity)

    def _inverse_date_deadline(self):
        for offer in self:
            offer.validity = (fields.Date.to_date(offer.date_deadline) - fields.Date.to_date(offer.create_date)).days

    def accept_offer(self):
        for offer in self:
            if offer.property_id.state in ["offer_accepted", "sold"]:
                raise UserError("Can't accept another offer for this property.")

            if offer.status == "accepted":
                continue

            offer.status = "accepted"
            offer.property_id.state = "offer_accepted"
            offer.property_id.selling_price = offer.price
            offer.property_id.buyer_id = offer.partner_id

    def refuse_offer(self):
        for offer in self:
            offer.status = "refused"
            offer.property_id.state = "offer_received"
            offer.property_id.selling_price = 0
            offer.property_id.buyer_id = ""

    @api.model
    def create(self, offer):
        property_id = self.env["estate.property"].browse(offer["property_id"])

        if offer["price"] < max(property_id.offer_ids.mapped("price") + [0]):
            raise UserError(_("Offer price needs to be higher than other offers."))

        property_id.state = "offer_received"
        return super().create(offer)
