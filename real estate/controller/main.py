#-*- coding: utf-8 -*-

from odoo import http, fields
from werkzeug.utils import redirect

number_of_record = 6

class EstatePropertyController(http.Controller):
    @http.route('/estate/index/', auth="public", website=True)
    def test(self):
        return redirect('/estate/index/1/')

    @http.route('/estate/index/<int:page>/', auth='public', website=True)
    def index(self, page):
        page = 1 if not page else page
        properties = http.request.env['estate.property']
        lim = page*number_of_record
        return http.request.render('real estate.index', {
            'properties': properties.search([], offset=(page-1)*number_of_record, limit=number_of_record),
            'page': page,
            'filtered': False,
        })

    @http.route('/estate/index/<model("estate.property"):estateProperty>/', auth='public', website=True)
    def property(self, estateProperty):
        return http.request.render('real estate.property', {
            'property': estateProperty
        })
    
    @http.route('/estate/index/get_date', auth='public')
    def filter_date(self, **kwargs):
        date = http.request.httprequest.form.get('date')
        url = "/estate/index/{}/1".format(date)
        return redirect(url)
    
    @http.route('/estate/index/<string:availablefrom>/<int:page>', auth='public', website=True)
    def property_with_date(self, availablefrom, page):
        properties = http.request.env['estate.property']
        # breakpoint()
        return http.request.render('real estate.index', {
            'properties': properties.search([('date_availability', '>',  fields.Date.to_date(availablefrom))]),
            'page': page,
            'filtered': True,
        })