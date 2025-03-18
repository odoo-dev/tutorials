from odoo import api, models, fields, exceptions

class PropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property Offer"

    price = fields.Float("Price")
    status = fields.Selection([("accepted", "Accepted"), ("refused", "Refused")], string="Status", copy=False)
    partner_id = fields.Many2one("res.partner", string = "Partner", required=True)
    property_id = fields.Many2one("estate.property", string = "Property", required=True)
    validity = fields.Integer("Validity (days)", default=7)
    date_deadline = fields.Date("Deadline", compute = "_compute_date_deadline", inverse = "_inverse_date_deadline")

    @api.depends("validity")
    def _compute_date_deadline(self):
        for record in self:
            record.date_deadline = fields.Date.add(record.create_day if hasattr(record, "create_day") else fields.Date.today(), days = record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            create_date = record.create_day if hasattr(record, "create_day") else fields.Date.today()
            record.validity = (record.date_deadline - create_date).days
    

    def action_accept_offer(self):
        for record in self:
            if record.status != "accepted":
                record.status = "accepted"
                record.property_id.state = "offer_accepted"
                record.property_id.buyer_id = record.partner_id
                record.property_id.selling_price = record.price
            else:
                raise exceptions.UserError("Only one offer can be accepted.")
            
    def action_refuse_offer(self):
        for record in self:
            record.status = "refused"
            record.property_id.state = "offer_refused"
    