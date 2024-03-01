#-*- coding: utf-8 -*-

from odoo import http, fields

number_of_record_per_page = 2

class EstatePropertyController(http.Controller):
    @http.route(['/estate/index/', '/estate/index/page/<int:page>'], auth='public', website=True)
    def index(self, page=1, date=None):
        page=int(page)
        page = 1 if not page else page
        properties = http.request.env['estate.property'].search([("state", "!=", "sold"), ("state", "!=", "canceled")])
        
        domain = [] if not date else [('date_availability', '<',  date)]

        total_properties = properties.search_count(domain)
        num_pages = total_properties/number_of_record_per_page
        num_pages = int(num_pages)+1 if num_pages > int(num_pages) else int(num_pages) 
        pager = http.request.website.pager(
            url="/estate/index/",
            total = total_properties,
            page=page,
            step = number_of_record_per_page,
            scope = num_pages
        )

        return http.request.render('estate.index', {
            'properties': properties.search(domain,  limit=number_of_record_per_page, offset=(page-1)*number_of_record_per_page),
            # 'page': page,
            # 'filtered': filtered,
            'pager': pager
        })

    @http.route('/estate/index/<model("estate.property"):estateProperty>/', auth='public', website=True)
    def property(self, estateProperty):
        return http.request.render('estate.property', {
            'property': estateProperty
        })
