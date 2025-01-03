from odoo import http
from odoo.http import request


class PropertyController(http.Controller):

    @http.route('/odoo/action-142/property', type='http', auth='public')
    def list_properties(self, page=1, **kwargs):
        properties_per_page = 6
        Property = request.env['estate.property'].sudo()
        total_properties = Property.search_count([])
        print(total_properties)
        offset = (int(page) - 1) * properties_per_page
        properties = Property.search([], limit=properties_per_page, offset=offset)
        print(properties)
        total_pages = (total_properties // properties_per_page) + (1 if total_properties % properties_per_page else 0)
        pager = {
            'current_page': page,
            'total_pages': total_pages,
            'url': '/odoo/action-142/property',
            'previous': page - 1 if page > 1 else None,
            'next': page + 1 if page < total_pages else None
        }
        return request.render('estate.property_list_template', {
            'properties': properties,
            'pager': pager,
        })
