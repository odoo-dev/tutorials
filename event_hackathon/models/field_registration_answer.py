from odoo import models, fields


class FieldRegistrationAnswer(models.Model):
    _name = "field.registration.answer"


    field_question_id = fields.Many2one(
            'field.question', ondelete='restrict', required=True,
            domain="[('event_ids', 'in', event_id)]")
    registration_id = fields.Many2one('event.registration', required=True, index=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', related='registration_id.partner_id')
    event_id = fields.Many2one('event.event', related='registration_id.event_id')
    value_text_box = fields.Text('Text answer')
    # question_type = fields.Selection(related='question_id.question_type')
    # value_answer_id = fields.Many2one('event.question.answer', string="Suggested answer")
