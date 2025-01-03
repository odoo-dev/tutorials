from odoo.http import request, route, Controller

class YourController(Controller):
    @route("/owl_example", auth="public")
    def standalone_app(self):
        return request.render(
            'owl_example.standalone_app',
            {
                'session_info': request.env['ir.http'].get_frontend_session_info(),
            }
        )
