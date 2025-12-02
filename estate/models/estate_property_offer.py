# 19.0-training-frtan
from typing import Self

from odoo import api, fields, models
from odoo.orm.types import ValuesType
from odoo.exceptions import UserError

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Offers inside Estate Property, a one2many field"
    _order = 'price desc'
    _price_positive = models.Constraint(
        'check (price > 0)',
        'The offer price must be strictly positive'
    )

    price = fields.Float()
    status = fields.Selection(selection=[("accepted", "Accepted"), ("refused", "Refused")])
    validity = fields.Integer(string="Validity (Days)", default=7)
    date_deadline = fields.Date(
        string="Deadline",
        compute="_compute_date_deadline",
        inverse="_inverse_date_deadline",
        store=True
    )

    property_id = fields.Many2one("estate.property", string="Property", required=True)
    property_type_id = fields.Many2one(related="property_id.property_type_id", string="Type", required=True)
    partner_id = fields.Many2one("res.partner", string="Buyer", required=True)

    @api.depends('validity')
    def _compute_date_deadline(self):
        for record in self:
            if record.create_date:
                record.date_deadline = fields.Date.add(record.create_date.date(), days=record.validity)
            else:
                record.date_deadline = fields.Date.add(fields.Date.today(), days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            set_date = record.create_date.date() if record.create_date else fields.Date.today()
            record.validity = (record.date_deadline - set_date).days

    @api.model
    def create(self, vals_list: list[ValuesType]):
        # vals is a list of dict
        for vals in vals_list:
            linked_property = self.env['estate.property'].browse(vals['property_id'])
            # solution 1, create the error in the estate.property.offer model
            # prices = linked_property.offer_ids.mapped('price')
            # if prices and self.price < min(prices):
            #         raise UserError(f"The offer must be higher than {max(prices)}")
            linked_property.change_state_when_offer_received(vals['price'])
        return super(EstatePropertyOffer, self).create(vals_list)


    def action_accept_estate_property_offer(self):
        self.property_id.selling_price = self.price
        self.status = "accepted"
        self.property_id.state = "offer_accepted"
        self.property_id.buyer_id = self.partner_id
        for record in self.property_id.offer_ids:
            if record.id != self.id:
                record.status = "refused"

    def action_refuse_estate_property_offer(self):
        self.status = "refused"