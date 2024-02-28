#-*- coding: utf-8 -*-

from odoo import http, fields
from werkzeug.utils import redirect

number_of_record_per_page = 6

class EstatePropertyController(http.Controller):
    @http.route(['/estate/index/', '/estate/index/page/<int:page>'], auth='public', website=True)
    def index(self, page=1, date=None):
        page=int(page)
        page = 1 if not page else page
        properties = http.request.env['estate.property'].search([("state", "!=", "sold"), ("state", "!=", "canceled")])
        lim = page*number_of_record_per_page
        total_properties = properties.search_count([])
        num_pages = total_properties/number_of_record_per_page
        num_pages = int(num_pages)+1 if num_pages > int(num_pages) else int(num_pages) 
        pager = http.request.website.pager(
            url="/estate/index/",
            total = total_properties,
            page=page,
            step = number_of_record_per_page,
            scope = num_pages
        )

        property_obj,filtered = (properties.search([], offset=(page-1)*number_of_record_per_page, limit=number_of_record_per_page), False) if not date\
            else (properties.search([('date_availability', '>',  date)]), True)
        return http.request.render('real estate.index', {
            'properties': property_obj,
            # 'page': page,
            # 'filtered': filtered,
            'pager': pager
        })

    @http.route('/estate/index/<model("estate.property"):estateProperty>/', auth='public', website=True)
    def property(self, estateProperty):
        return http.request.render('real estate.property', {
            'property': estateProperty
        })
