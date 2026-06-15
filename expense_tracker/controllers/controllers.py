from odoo import http
from odoo.http import request


class OwlPlayground(http.Controller):
    @http.route(['/expense_tracker'], type='http', auth='public')
    def show_playground(self):
        """
        Renders the owl playground page
        """
        return request.render('expense_tracker.playground')
