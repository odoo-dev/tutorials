from odoo import api, fields, models
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class estatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate property offer model"

    price = fields.Float(string="Price")
    status = fields.Selection(
        string="Status",
        selection=[("accepted", "Accepted"), ("refused", "Refused")],
        copy=False,
    )
    partner_id = fields.Many2one("res.partner", string="Partner")
    property_id = fields.Many2one("estate.property")
    validity = fields.Integer(string="Validity (days)", default=7)
    date_deadline = fields.Date(
        string="Date", compute="_compute_date_deadline", inverse="_set_validity"
    )

    # constraints
    _sql_constraints = [
        (
            "check_price",
            "CHECK(price>=0)",
            "The offer price is always a positive number",
        )
    ]

    @api.depends("validity", "create_date")
    def _compute_date_deadline(self):
        for record in self:
            if record.create_date:
                record.date_deadline = record.create_date + relativedelta(
                    days=record.validity
                )
            else:
                record.date_deadline = fields.Date.today() + relativedelta(
                    days=record.validity
                )

    def _set_validity(self):
        for record in self:
            if record.create_date:
                record.validity = (
                    record.date_deadline - record.create_date.date()
                ).days
            else:
                record.validity = (record.date_deadline - fields.Date.today()).days

    def action_confirm(self):
        for record in self:
            record.status = "accepted"
            record.property_id.selling_price = record.price
            record.property_id.buyer_id = record.partner_id
            for offer in record.property_id.offer_ids:
                if not offer.id == record.id:
                    offer.status = "refused"
            return True

    def action_cancel(self):
        for record in self:
            record.status = "refused"
            return True
