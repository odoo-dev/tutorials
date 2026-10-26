from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Offer for the properties of the estate module"
    _order = "id desc"

    price = fields.Float()
    status = fields.Selection(
        string="Status",
        selection=[('accepted', 'Accepted'), ('refused', 'Refused')],
        help='Current status of the offer (Accepted or Refused).'
    )
    partner_id = fields.Many2one("res.partner", string="Partner")
    property_id = fields.Many2one("estate.property", string="Properties")
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(compute="_compute_date_deadline", inverse="_inverse_date_deadline")
    property_type_id = fields.Many2one(related="property_id.property_type_id", store=True)

    @api.depends("validity")
    def _compute_date_deadline(self):
        for record in self:
            record.date_deadline = fields.Date.add(record.create_date or fields.Date.today(), days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            record.validity = (record.date_deadline - fields.Date.today()).days

    def action_accept_offer(self):
        for record in self:
            if record.status == 'refused':
                raise UserError("Can't refuse an already accepted offer")
            if record.property_id.state == 'offer_accepted':
                raise UserError("Can only accept one offer!")
            record.status = 'accepted'
            record.property_id.state = 'offer_accepted'
            record.property_id.selling_price = record.price
            record.property_id.buyer_id = record.partner_id

    def action_refuse_offer(self):
        for record in self:
            if record.status == 'accepted':
                raise UserError("Can't accept an already refused offer")
            record.status = 'refused'

    _check_offer_price = models.Constraint(
        'CHECK(price > 0)',
        'An offer price must be strictly positive'
    )

    @api.model
    def create(self, vals):
        if float_compare(self.env['estate.property'].browse(vals[0]['property_id']).best_price, vals[0]['price'], precision_digits=2) == 1:
            raise UserError("New offer must beat precedent offers")
        self.env['estate.property'].browse(vals[0]['property_id']).state = 'offer_received'
        return super().create(vals)
