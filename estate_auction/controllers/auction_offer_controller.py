from odoo import http
from odoo.http import request
from odoo.exceptions import UserError

class AuctionOfferController(http.Controller):

    @http.route('/submit_bid_form', type='http', auth='public', website=True, csrf=False)
    def submit_bid_form(self, **post):
        try:
            property_id = int(post.get("property_id"))
            partner_id = post.get("partner_id")
            bid_amount = float(post.get("bid_amount"))

            if bid_amount <= 0:
                return request.render("website.404")

            property_rec = request.env['estate.property'].sudo().browse(property_id)
            if not property_rec.exists():
                return request.not_found()

            offer = {
                'price': bid_amount,
                'partner_id': partner_id,
                'property_id': property_id,
            }
            request.env['estate.property.offer'].sudo().create(offer)
            return request.redirect("/properties")

        except Exception as e:
            return request.render("website.500", {'error': str(e)})
