from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class CustomerPortalExtended(CustomerPortal):
    
    def _prepare_my_account_rendering_values(self, redirect='/my', **kwargs):
        """Override to add custom fields from all registered events"""
        values = super(CustomerPortalExtended, self)._prepare_my_account_rendering_values(redirect=redirect, **kwargs)
        
        partner = request.env.user.partner_id
        
        registrations = request.env['event.registration'].sudo().search([
            ('partner_id', '=', partner.id)
        ])
        
        event_ids = registrations.mapped('event_id').ids
        event_type_ids = registrations.mapped('event_id.event_type_id').ids
        
        custom_fields = []
        seen_questions = {}
        
        if event_ids or event_type_ids:
            questions = request.env['field.question'].sudo().search([
                '|',
                ('event_ids', 'in', event_ids),
                ('event_type_ids', 'in', event_type_ids)
            ])
            
            for question in questions:
                if question.title in seen_questions:
                    existing_entry = seen_questions[question.title]
                    for reg in registrations:
                        if (question.event_ids and reg.event_id.id in question.event_ids.ids) or \
                           (question.event_type_ids and reg.event_id.event_type_id.id in question.event_type_ids.ids):
                            if reg.event_id.name not in existing_entry['related_events']:
                                existing_entry['related_events'].append(reg.event_id.name)
                    continue
                
                answer = request.env['field.registration.answer'].sudo().search([
                    ('partner_id', '=', partner.id),
                    ('field_question_id', '=', question.id)
                ], limit=1)
                
                related_events = []
                for reg in registrations:
                    if (question.event_ids and reg.event_id.id in question.event_ids.ids) or \
                       (question.event_type_ids and reg.event_id.event_type_id.id in question.event_type_ids.ids):
                        related_events.append(reg.event_id.name)
                
                field_entry = {
                    'question': question,
                    'answer': answer,
                    'related_events': related_events,
                }
                
                custom_fields.append(field_entry)
                seen_questions[question.title] = field_entry
        
        values.update({
            'custom_fields': custom_fields,
            'has_registrations': bool(registrations),
        })
        
        return values
    
    @http.route('/my/address/submit', type='http', methods=['POST'], auth='user', website=True, sitemap=False)
    def portal_address_submit(self, partner_id=None, **form_data):
        """Override to handle custom field answers"""
        result = super(CustomerPortalExtended, self).portal_address_submit(partner_id=partner_id, **form_data)
        
        partner = request.env.user.partner_id
        registrations = request.env['event.registration'].sudo().search([
            ('partner_id', '=', partner.id)
        ])
        
        if registrations:
            event_ids = registrations.mapped('event_id').ids
            event_type_ids = registrations.mapped('event_id.event_type_id').ids
            
            questions = request.env['field.question'].sudo().search([
                '|',
                ('event_ids', 'in', event_ids),
                ('event_type_ids', 'in', event_type_ids)
            ])
            
            processed_questions = {}
            
            for question in questions:
                field_key = f'custom_field_{question.id}'
                
                if question.title in processed_questions:
                    first_question = processed_questions[question.title]
                    first_field_key = f'custom_field_{first_question.id}'
                    answer_value = form_data.get(first_field_key)
                else:
                    answer_value = form_data.get(field_key)
                    processed_questions[question.title] = question
                
                if answer_value is not None:
                    related_registration = None
                    for reg in registrations:
                        if (question.event_ids and reg.event_id.id in question.event_ids.ids) or \
                           (question.event_type_ids and reg.event_id.event_type_id.id in question.event_type_ids.ids):
                            related_registration = reg
                            break
                    
                    if not related_registration:
                        continue
                    
                    answer = request.env['field.registration.answer'].sudo().search([
                        ('partner_id', '=', partner.id),
                        ('field_question_id', '=', question.id)
                    ], limit=1)
                    
                    answer_vals = {
                        'field_question_id': question.id,
                        'registration_id': related_registration.id,
                        'value_text_box': answer_value,
                    }
                    
                    if answer:
                        answer.sudo().write(answer_vals)
                    else:
                        request.env['field.registration.answer'].sudo().create(answer_vals)
        
        return result