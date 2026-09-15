from odoo import api, fields, models
from odoo.exceptions import UserError


class PropertyType(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property Offer"
    _order = "price desc"

    _check_positive_price = models.Constraint(
        "CHECK(price > 0)",
        "The offer price must be stricly positive",
    )

    price = fields.Float()
    status = fields.Selection(
        copy=False,
        selection=[("accepted", "Accepted"), ("refused", "Refused")],
    )
    partner_id = fields.Many2one("res.partner", required=True)
    property_id = fields.Many2one("estate.property", required=True)
    property_type_id = fields.Many2one(
        related="property_id.property_type_id",
        store=True,
    )
    validity = fields.Integer("Validity (Days)", default=7)
    date_deadline = fields.Date(
        compute="_compute_deadline",
        inverse="_inverse_deadline",
    )

    @api.depends("validity")
    def _compute_deadline(self):
        for record in self:
            create_date = record.create_date or fields.Date.today()
            record.date_deadline = fields.Date.add(create_date, days=record.validity)

    def _inverse_deadline(self):
        for record in self:
            create_date = record.create_date or fields.Date.today()
            record.validity = (
                record.date_deadline - fields.Date.to_date(create_date)
            ).days

    # ------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            property_obj = self.env["estate.property"].browse(vals.get("property_id"))
            if property_obj.offer_ids:
                max_offer = max(property_obj.offer_ids.mapped("price"))
                if int(vals.get("price")) <= max_offer:
                    raise UserError(self.env._("Offer with higher price already exist"))

        records = super().create(vals_list)

        for record in records:
            if record.property_id:
                record.property_id.state = "offer_received"

        return records

    # ------------------------------------------------------------
    # ACTIONS
    # ------------------------------------------------------------

    def action_accept_offer(self):
        self.status = "accepted"
        self.property_id.selling_price = self.price
        self.property_id.buyer_id = self.partner_id
        self.property_id.state = "offer_accepted"

        for offer in self.property_id.offer_ids:
            if offer != self:
                offer.status = "refused"

        return True

    def action_refuse_offer(self):
        for record in self:
            record.status = "refused"
        return True
