from odoo import api, fields, models
from dateutil.relativedelta import relativedelta


class EstatePropertyOfferModel(models.Model):
    _name = "estate_property_offer"
    _description = "Estate property offer"

    price = fields.Float()
    status = fields.Selection([("accepted", "Accepted"), ("refused", "Refused")], copy=False)
    partner_id = fields.Many2one("res.partner", required=True)
    property_id = fields.Many2one("estate_property", required=True)

    validity = fields.Integer(default=7)
    create_date = fields.Date(default=fields.Date.today())
    date_deadline = fields.Date(compute="_compute_deadline", inverse="_inverse_deadline")

    @api.depends("validity")
    def _compute_deadline(self):
        for record in self:
            record.date_deadline = record.create_date + relativedelta(days=record.validity)

    def _inverse_deadline(self):
        for record in self:
            record.validity = (self.date_deadline - fields.Date.today()).days
