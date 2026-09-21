from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class EstatePropertyOffer(models.Model):
    ## Private attributes ##
    _name = "estate.property.offer"
    _description = "Real estate property offers"
    _order = "price desc"

    ## Fields declaration ##
    price = fields.Float()
    status = fields.Selection(
        string="Status",
        selection=[
            ("accepted", "Accepted"),
            ("refused", "Refused"),
        ],
        copy=False,
    )
    partner_id = fields.Many2one("res.partner", required=True)
    property_id = fields.Many2one("estate.property", required=True)
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(
        compute="_compute_date_deadline",
        inverse="_inverse_date_deadline",
    )
    property_type_id = fields.Many2one(related="property_id.property_type_id")

    ## SQL constraints ##
    _check_price_positive = models.Constraint(
        "CHECK(price > 0)",
        "Offer price must always be positive",
    )

    ## Compute methods ##
    @api.depends("validity")
    def _compute_date_deadline(self):
        for record in self:
            start_date = record.create_date or fields.Date.today()
            record.date_deadline = start_date + relativedelta(days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            if record.date_deadline:
                record.validity = record._get_validity_days()

    ## Constraints and onchanges ##
    # inverse doesn't update the UI when date_deadline changes,
    # so we define an additional onchange to not confuse users
    @api.onchange("date_deadline")
    def _onchange_date_deadline(self):
        self.validity = self._get_validity_days()

    ## CRUD methods ##
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            estate_property = self.env["estate.property"].browse(vals["property_id"])
            if estate_property.state == "new":
                estate_property.state = "offer_received"
        return super().create(vals_list)

    ## Action methods ##
    def action_accept(self):
        # prevent accepting multiple offers
        self.ensure_one()

        # no need to process an already accepted offer
        if self.status == "accepted":
            return True

        # ensure no other offer is already accepted
        accepted_offers = self.property_id.offer_ids.filtered(
            lambda offer: offer.status == "accepted",
        )
        if len(accepted_offers) > 0:
            raise UserError(_("Another offer was already accepted"))

        self.status = "accepted"
        self.property_id.buyer_id = self.partner_id
        self.property_id.selling_price = self.price
        self.property_id.state = "offer_accepted"
        return True

    def action_refuse(self):
        for record in self:
            record.status = "refused"
        return True

    ## Business methods ##
    def _get_validity_days(self):
        start_date = fields.Date.today()
        if self.create_date:
            start_date = self.create_date.date()
        delta = self.date_deadline - start_date
        return delta.days
