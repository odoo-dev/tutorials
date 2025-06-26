from odoo import fields, models


class EstateProperty(models.Model):
    _inherit = "estate.property"

    property_sell_type = fields.Selection(
        [("auction", "Auction"), ("regular", "Regular")], default="auction"
    )
    auction_state = fields.Selection(
        [
            ("template", "Template"),
            ("auction", "Auction"),
            ("sold", "Sold"),
        ],
        default="template",
    )
    auction_end_time = fields.Datetime(string="End Time")
    highest_offer = fields.Float(string="Highest Offer", readonly=True)
    highest_bidder = fields.Float(string="Highest Bidder", readonly=True)

    def action_start_auction(self):
        self.auction_state = "auction"
