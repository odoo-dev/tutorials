from odoo import api, fields, models
from odoo.exceptions import UserError


class EstatePropertyTag(models.Model):
    _name = "estate.property.offer"
    _description = "This is an offer made by a partner to buy the property"

    price = fields.Float(required=True)
    status = fields.Selection(copy=False, selection=[("accepted", "Accepted"), ("refused", "Refused")])
    partner_id = fields.Many2one("res.partner", string = "Partner", required=True)
    property_id = fields.Many2one("estate.property", "Property", required=True)
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(compute="_compute_deadline", inverse="_inverse_deadline")

    @api.depends("validity")
    def _compute_deadline(self):
        for record in self:
            if not record.create:
                record.date_deadline = fields.Datetime.add(record.create_date.date(), days=record.validity)
            else:
                record.date_deadline = fields.Datetime.add(fields.Datetime.today(), days=record.validity)
    
    @api.depends("date_deadline")
    def _inverse_deadline(self):
        for record in self:
                record.validity = (record.date_deadline - record.create_date.date()).days
    
    def accept_offer(self):
        for record in self:
            if record.status == "accepted" or record.property_id.stage in ("cancelled", "sold", "offer accepted"):
                UserError(self.env._("Property not available"))
                return False
            record.status = "accepted"
            record.property_id.buyer_id = record.partner_id
            record.property_id.selling_price = record.price
            record.property_id.stage = "offer accepted"
        return True
    
    def refuse_offer(self):
        for record in self:
            record.status = "refused"
        return True
    
    _check_price = models.Constraint(
        'CHECK (price > 0)',
        'Offer price must be strictly positive'
    )
