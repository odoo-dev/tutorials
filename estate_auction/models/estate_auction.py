from odoo import fields, models


class EstateProperty(models.Model):
    _inherit = "estate.property"

    sale_mode = fields.Selection(
        [
            ("regular", "Regular"),
            ("auction", "Auction"),
        ],
        default="regular",
        required=True,
    )
    auction_end_time = fields.Datetime(string="End Time")
    highest_offer = fields.Float(string="Highest Offer", readonly=True)
    highest_bidder_id = fields.Many2one(
        "res.partner",
        string="Highest Bidder",
        readonly=True
    )
