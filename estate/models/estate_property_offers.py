from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class PropertyOffer(models.Model):
    _name = "estate.property.offers"
    _description = "this model is used to define the offers received to the property"

    price = fields.Float()
    status = fields.Selection(
        [("accepted", "Accepted"), ("refused", "Refused"), ("pending", "Pending")],
        default="pending",
    )
    partner_id = fields.Many2one("res.partner", required=True)
    property_id = fields.Many2one("estate.property", required=True, ondelete="cascade")
    deadline = fields.Date(
        default=date.today(),
        copy=False,
        compute="_compute_deadline",
        inverse="_inverse_deadline",
        store=True,
    )
    validity_days = fields.Integer(default=7, copy=False)

    @api.depends("validity_days")
    def _compute_deadline(self):
        for records in self:
            base_date = (
                records.create_date.date()
                if records.create_date
                else fields.Date.today()
            )
            records.deadline = base_date + relativedelta(days=records.validity_days)

    def _inverse_deadline(self):
        for records in self:
            base_date = (
                records.create_date.date()
                if records.create_date
                else fields.Date.today()
            )
            diff = relativedelta(records.deadline, base_date)
            records.validity_days = diff.days

    def action_confirm(self):
        self.status = "accepted"
        self.property_id.buyer = self.partner_id
        self.property_id.selling_price = self.price
        offers = self.env["estate.property.offers"].browse(
            self.env["estate.property.offers"].search([]).ids
        )
        for record in offers:
            if record.id != self.id:
                record.status = "refused"

    def action_cancel(self):
        self.status = "refused"
