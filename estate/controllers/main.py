from odoo.http import request, route, Controller

class EstateProperty(Controller):

    @route(['/properties', '/properties/page/<int:page>'], type='http', website=True, auth='public')
    def display_properties(self, **kwargs):
        page = int(kwargs.get('page', 1))
        offset = (page - 1) * 6
        date_picked = kwargs.get('filter_properties')

        domain = [('state', '!=', 'canceled')]
        if date_picked:
            domain.append(('create_date', '>=', date_picked))

        properties = request.env['estate.property'].search(domain, offset=offset, limit=6)

        total_properties = request.env['estate.property'].search_count([('state', '!=', 'canceled')])

        pager = request.website.pager(url="/properties", total=total_properties, page=page, step=6)

        return request.render("estate.estate_property_page_view", {'properties': properties, 'pager': pager})
    
    @route('/estate/property/<int:property_id>', type='http', auth='public', website=True)
    def display_individual_property_details(self, property_id):
        property = request.env['estate.property'].browse(property_id)

        return request.render('estate.estate_property_form_page_view', {'property': property})
