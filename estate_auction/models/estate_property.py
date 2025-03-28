from odoo import fields, models


class EstateProperty(models.Model):
    _inherit = 'estate.property'

    auction_end_time = fields.Datetime(string='End Time')
    auction_highest_offer = fields.Float(string='Highest Offer', readonly=True)
    auction_highest_bidder = fields.Many2one(comodel_name='res.partner', string='Highest Bidder', readonly=True)
    property_sale_type = fields.Selection(
        selection=[
            ('auction','Auction'),
            ('regular','Regular')
        ],
        default='regular'
    )
    auction_state = fields.Selection(
        selection=[
            ('template','Auction'),
            ('auction','Auction Start'),
            ('sold','Sold')
        ],
        default='template',
        tracking=True
    )

    def action_auction_start(self):
        pass