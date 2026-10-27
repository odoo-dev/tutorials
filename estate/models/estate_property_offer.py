from odoo import api, exceptions, fields, models


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Listing of offers for a property"

    price = fields.Float()
    status = fields.Selection(copy=False, selection=[("accepted", "Accepted"), ("rejected", "Rejected")])
    partner_id = fields.Many2one("res.partner", required=True)
    property_id = fields.Many2one("estate.property", required=True)
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(compute="_compute_date_deadline", inverse="_inverse_date_deadline")

    @api.depends("create_date", "validity")
    def _compute_date_deadline(self):
        for record in self:
            if not record.create_date:
                record.date_deadline = fields.Date.add(fields.Date.today(), days=record.validity)
            else:
                record.date_deadline = fields.Date.add(record.create_date, days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            if not record.create_date:
                record.validity = (record.date_deadline - fields.Date.today()).days
            else:
                record.validity = (record.date_deadline - fields.Date.to_date(record.create_date)).days

    def action_accept_offer(self):
        if self.property_id.state in {"sold", "offer accepted", "cancelled"}:
            raise exceptions.UserError(self.env._("No offer can be accepted for this property."))
        else:
            self.status = "accepted"
            self.property_id.state = "sold"
            self.property_id.selling_price = self.price
            self.property_id.buyer_id = self.partner_id
        return True

    def action_reject_offer(self):
        self.status = "rejected"
