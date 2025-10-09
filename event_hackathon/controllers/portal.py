from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class CustomerPortalInherit(CustomerPortal):

    @http.route(['/my/account'], type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
        """Override to add custom questions to context"""
        response = super(CustomerPortalInherit, self).account(redirect=redirect, **post)
        
        if request.httprequest.method == 'GET':
            partner = request.env.user.partner_id
            
            # Get all custom questions (you can filter by event type if needed)
            custom_questions = request.env['partner.question'].sudo().search([])
            
            # Get existing answers for this partner
            existing_answers = {}
            for answer in partner.partner_answer_ids:
                existing_answers[answer.question_id.id] = answer.value_text_box
            
            # Add to context
            if hasattr(response, 'qcontext'):
                response.qcontext.update({
                    'custom_questions': custom_questions,
                    'existing_answers': existing_answers,
                })
        
        return response