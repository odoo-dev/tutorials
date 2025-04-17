# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class EstateProperty(models.Model):
    _inherit = "estate.property"

    sale_type = fields.Selection(
        string="Sale Type",
        selection=[("auction", "Auction"), ("regular", "Regular")],
        default="regular",
    )
    auction_status = fields.Selection(
        string="Auction Status",
        selection=[("template", "Template"), ("auction", "Auction"), ("sold", "Sold")],
        default="template",
    )
    auction_end_time = fields.Datetime(string="End Time")
    highest_auction_bidder = fields.Char(
        string="Highest Bidder", compute="_compute_highest_bidder"
    )
    is_auction_start = fields.Boolean(string="Is Auction Start")

    @api.depends("best_price")
    def _compute_highest_bidder(self):
        for record in self:
            best_offer = max(
                record.offer_ids, key=lambda offer: offer.price, default=False
            )
            record.highest_auction_bidder = (
                best_offer.partner_id.name if best_offer else ""
            )

    def action_start_auction(self):
        if self.auction_end_time:
            self.is_auction_start = True
            self.auction_status = "auction"
        else:
            raise UserError("You first need to set the auction end time to start the auction.")
