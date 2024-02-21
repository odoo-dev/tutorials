from odoo import api, fields, models
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError


class estatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate property offer model"
    _order = "price desc"

    price = fields.Float(string="Price")
    status = fields.Selection(
        string="Status",
        selection=[("accepted", "Accepted"), ("refused", "Refused")],
        copy=False,
    )
    partner_id = fields.Many2one("res.partner", string="Partner")
    property_id = fields.Many2one("estate.property")
    property_type_id = fields.Many2one(
        related="property_id.property_type_id", store=True
    )
    validity = fields.Integer(string="Validity (days)", default=7)
    date_deadline = fields.Date(
        string="Deadline", compute="_compute_date_deadline", inverse="_set_validity"
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
            # breakpoint()
            record.property_id.state = "offer_accepted"
            for offer in record.property_id.offer_ids:
                if not offer.id == record.id:
                    offer.status = "refused"
            return True

    def action_cancel(self):
        for record in self:
            record.status = "refused"
            return True

    @api.model
    def create(self, vals):
        if "property_id" in vals:
            property_obj = self.env["estate.property"].browse(vals["property_id"])

            if "price" in vals:
                if vals["price"] < property_obj.best_price:
                    raise UserError(
                        "You cannot create an offer with a lower amount than the current best offer."
                    )

            property_obj.state = "offer_recieved"
        return super(estatePropertyOffer, self).create(vals)
