from odoo import api, models, fields

class PropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property Offer"

    price = fields.Float("Price")
    status = fields.Selection([("accepted", "Accepted"), ("refused", "Refused")], string="Selection", copy=False)
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
    
    