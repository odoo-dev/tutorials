from odoo import api, fields, models


class EstatePropertyAuction(models.Model):
    _inherit = 'estate.property'

    sale_type = fields.Selection(
        [
            ('auction', 'Auction'),
            ('regular', 'Regular')
        ],
        string="Sale Type", default="regular")
    auction_state = fields.Selection([
        ('template', 'Template'),
        ('auction', 'Auction'),
        ('sold', 'Sold'),
    ], string="Auction Status", default="template", tracking=True)

    auction_starttime = fields.Datetime(string="Start time")
    auction_endtime = fields.Datetime(string="End time")
    highest_offer = fields.Float(string="Highest Offer", readonly=True)
    highest_bidder = fields.Char(string="Highest Bidder", readonly=True)

    def action_auction_start_button(self):
        pass
