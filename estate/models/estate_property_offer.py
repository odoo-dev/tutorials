from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import date_utils


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Real Estate Property Offer"
    _order = "price desc"

    price = fields.Float()
    status = fields.Selection([('accepted', 'Accepted'), ('refused', 'Refused')], copy=False)
    date_deadline = fields.Date(compute='_compute_date_deadline', inverse='_inverse_date_deadline')
    validity = fields.Integer()
    property_type_id = fields.Many2one(related="property_id.property_type_id")
    partner_id = fields.Many2one("res.partner", required=True)
    property_id = fields.Many2one("estate.property", required=True)

    _check_price = models.Constraint(
        'CHECK(price > 0)',
        'Prices must be positive',
    )

    @api.depends('validity')
    def _compute_date_deadline(self):
        for offer in self:
            offer.date_deadline = date_utils.add(fields.Date.today(), days=offer.validity)

    def _inverse_date_deadline(self):
        for offer in self:
            offer.validity = (offer.date_deadline - fields.Date.today()).days

    def accept(self):
        self.status = "accepted"
        self.property_id.buyer_id = self.partner_id
        self.property_id.selling_price = self.price

    def deny(self):
        self.status = "refused"

    @api.model
    def create(self, vals):
        for val in vals:
            property = self.env['estate.property'].browse(val['property_id'])
            if val["price"] < property.best_price:
                raise UserError(_("You can not create an offer if it is not the biggest one!"))
            property.state = "received"
        return super().create(vals)
