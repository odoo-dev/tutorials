from odoo import api, models, fields
from datetime import date

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property Offer"

    price = fields.Float(string="Price", required=True)
    status = fields.Selection(
        string='Status',
        selection=[
            ('accepted', 'Accepted'),
            ('refussed', 'Refused')
        ],
        copy=False
    )
    partner_id = fields.Many2one("res.partner", string="Partener", required=True)
    property_id = fields.Many2one("estate.property", string="Property Id", required=True)
    validity = fields.Integer(string="Validity", default=7)
    date_deadline = fields.Date(compute="_compute_total", inverse="_inverse_dead", string="Deadline")

    @api.depends("validity")
    def _compute_total(self):
        for record in self:
            if record.create_date:
                record.date_deadline = fields.Date.add(record.create_date, days=record.validity)
            else:
                record.date_deadline = fields.Date.add(date.today(), days=record.validity)

    def _inverse_dead(self):
        for record in self:
            record.validity = fields.Date.subtract(record.date_deadline-fields.Date.to_date(record.create_date)).days