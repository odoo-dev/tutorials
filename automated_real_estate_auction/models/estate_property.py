import logging
from odoo import fields, models, api

_logger = logging.getLogger(__name__)

class EstateProperty(models.Model):
    _inherit = "estate.property"

    invoice_id = fields.Many2one('account.move', string="Invoice", readonly=True)

    state = fields.Selection(
        [('auction', 'Auction'), ('regular', 'Regular')],
        default='regular'
    )

    end_time = fields.Datetime(string="End Time", store=True)
    highest_offer = fields.Integer(string="Highest Offer", readonly=True, store=True, compute="_compute_highest_offer")
    highest_bidder = fields.Many2one('res.partner', string="Highest Bidder", readonly=True, store=True, compute="_compute_highest_offer")

    auction_started = fields.Selection(
        [('template', 'Template'), ('auction', 'Auction'), ('sold', 'Sold')],
        default='template'
    )

    def action_auction(self):
        for record in self:
            record.auction_started = 'auction'

    def action_invoice(self):
        # breakpoint()
    # Create invoice for the property
        invoice_vals = {
            'move_type': 'out_invoice',  # Customer invoice
            'partner_id': self.buyer_id.id,  # The buyer as the customer
            'name' : f'INV/2025/{self.id}',
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {
                'name': f"Property: {self.name}",
                'quantity': 1,
                'price_unit': self.selling_price,
            })],
        }

        # Create the invoice
        invoice = self.env['account.move'].create(invoice_vals)

        # Open the invoice form view
        return {
            'name': 'Customer Invoice',
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'type': 'ir.actions.act_window',
        }

    @api.depends("offer_ids.price")
    def _compute_highest_offer(self):
        for record in self:
            best_offer = record.offer_ids.sorted(lambda o: o.price, reverse=True)
            record.highest_offer = best_offer[0].price if best_offer else 0
            record.highest_bidder = best_offer[0].partner_id if best_offer else False

    def _cron_check_auction_end(self):
        _logger.info("Running _cron_check_auction_end...")

        auctions = self.search([
            ('state', '=', 'auction'),
            ('auction_started', '=', 'auction'),
            ('status', 'not in', ['sold', 'cancelled']),
            ('end_time', '<=', fields.Datetime.now())
        ])

        _logger.info(f"Found {len(auctions)} auctions that have ended.")

        for auction in auctions:
            _logger.info(f"Processing auction {auction.id}: {auction.name}")

            if auction.highest_bidder and auction.highest_offer > 0:
                best_price = auction.offer_ids.filtered(
                    lambda o: o.partner_id == auction.highest_bidder and
                    o.price == auction.highest_offer and
                    o.status not in ['offer_accepted', 'refused']
                )

                if best_price:
                    _logger.info(f"Accepting highest offer {best_price[0].price} from {auction.highest_bidder.name}")
                    best_price[0].action_accept(from_cron=True)  # Accept the highest bid
                    auction.write({
                        'status': 'sold',
                        'auction_started': 'sold',
                        'selling_price': auction.highest_offer,
                        'buyer_id': auction.highest_bidder.id,
                    })
                else:
                    _logger.warning(f"No valid best_offer found for auction {auction.id}")
            else:
                _logger.info(f"Auction {auction.id} has no valid bids, cancelling.")
                auction.write({
                    'status': 'cancelled',
                    'auction_started': 'template',
                })
