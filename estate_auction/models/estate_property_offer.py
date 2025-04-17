# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api
from odoo.exceptions import UserError


class EstatePropertyOffer(models.Model):
    _inherit = "estate.property.offer"

    def action_accepted(self):
        for record in self:
            if record.property_id.sale_type == "auction":
                raise UserError("You cannot accept offer manually for auction properties.")
            return super(EstatePropertyOffer, record).action_accepted()

    def action_refused(self):
        for record in self:
            if record.property_id.sale_type == "auction":
                raise UserError("You cannot refuse offer manually for auction properties.")
            return super(EstatePropertyOffer, record).action_refused()

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            if record.property_id.sale_type == "auction":
                if record.price < record.property_id.expected_price:
                    raise UserError("You cannot create an offer lower than an expected price.")

                if record.property_id.state == "new":
                    record.property_id.state = "offer_received"

                record.property_id.message_post(body=f"New offer of {record.price} received from {record.partner_id.name}.")

        return records
