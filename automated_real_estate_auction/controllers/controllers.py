# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request

class EstateAuction(http.Controller):

    @http.route('/create_offer/<int:property_id>', type='http', auth='user', website=True)
    def create_offer(self, property_id, **kwargs):
        # Fetch the property and logged-in user
        property = request.env['estate.property'].sudo().browse(property_id)
        user = request.env.user

        return request.render('automated_real_estate_auction.create_offer_template', {
            'property': property,
            'user': user,
        })

    @http.route('/submit_offer', type='http', auth='user', methods=['POST'], website=True)
    def submit_offer(self, **post):
        property_id = int(post.get('property_id'))
        offer_amount = float(post.get('amount'))

        # Create the offer
        request.env['estate.property.offer'].sudo().create({
            'property_id': property_id,
            'partner_id': request.env.user.partner_id.id,
            'price': offer_amount,
        })

        # Redirect to the success page
        return request.redirect('/offer_success')

    @http.route('/offer_success', type='http', auth='user', website=True)
    def offer_success(self, **kwargs):
        return request.render("automated_real_estate_auction.offer_success_template")

    @http.route(['/properties', '/properties/page/<int:page>'], auth='public', website=True)
    def list_properties(self, page=1, **kwargs):
        property = http.request.env['estate.property'].sudo()
        per_page = 6

        # Start with base domain
        domain = [('status', 'not in', ['sold', 'cancelled'])]

        # Check if auction filter is active from URL params
        auction_filter = kwargs.get('auction') == 'true'
        if auction_filter:
            domain.append(('state', '=', 'auction'))  # Adjust field as per your model

        # Fetch filtered properties
        total_properties = property.search_count(domain)
        properties = property.search(domain, offset=(page - 1) * per_page, limit=per_page)

        # Pager
        pager = http.request.website.pager(
            url='/properties',
            total=total_properties,
            page=page,
            step=per_page,
            url_args={'auction': 'true'} if auction_filter else {}  # Maintain filter on pagination links
        )

        # Render the listing template
        return http.request.render(
            'estate.property_listing_template',
            {
                'properties': properties,
                'pager': pager,
                'auction_filter': auction_filter  # Send flag to template
            }
        )