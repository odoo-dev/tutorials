from odoo import api, fields, models
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Property Offer"
    _order = "price desc"

    price = fields.Float("Price", required=True)
    status = fields.Selection(selection=[("accepted", "Accepted"), ("refused", "Refused")], copy=False)
    property_id = fields.Many2one("estate.property", string="Property", required=True)
    property_type_id = fields.Many2one(related="property_id.property_type_id", store=True)
    partner_id = fields.Many2one("res.partner", string="Partner", required=True)
    validity = fields.Integer("Validity (days)", default=7)
    date_deadline = fields.Date("Deadline", compute="_compute_deadline", inverse="_inverse_deadline")

    _sql_constraints = [
        ("check_offer_price", "CHECK(price > 0)", "The offer price must be positive.")
    ]

    @api.depends("create_date", "validity")
    def _compute_deadline(self):
        for record in self:
            if record.create_date:
                record.date_deadline = record.create_date + relativedelta(
                    days=record.validity
                )

    def _inverse_deadline(self):
        for record in self:
            if record.date_deadline and record.create_date:
                record.validity = (
                    record.date_deadline - record.create_date.date()
                ).days

    def action_refuse(self):
        self.status = "refused"
        count_accepted = self.search_count(
            [("property_id", "=", self.property_id.id), ("status", "=", "accepted")]
        )
        if count_accepted == 0:
            self.property_id.state = "offer_received"

    def action_accept(self):
        count_accepted = self.search_count(
            [("property_id", "=", self.property_id.id), ("status", "=", "accepted")]
        )
        if count_accepted:
            raise UserError(
                "There is already an accepted offer for this property")
        else:
            self.status = "accepted"

        self.property_id.buyer_id = self.partner_id
        self.property_id.selling_price = self.price
        self.property_id.state = "offer_accepted"

    @api.model_create_multi
    def create(self, vals_list):

        records = super().create(vals_list)

        properties = records.mapped("property_id")
        properties.filtered(lambda p: p.state == "new").write(
            {"state": "offer_received"}
        )

        return records
