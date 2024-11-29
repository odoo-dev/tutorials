from odoo import http
class EstatePropertyController(http.Controller):
    @http.route('/estate_website_properties', auth='public', website=True)
    def properties(self):
        return http.request.render('estate.estate_property_website_view_id')
