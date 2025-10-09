from odoo import models, fields


class FieldQuestion(models.Model):
    _name = "field.question"
    _order = "title"

    title = fields.Char(required=True, translate=True)
    event_type_ids = fields.Many2many('event.type', string='Event Types', copy=False)
    event_ids = fields.Many2many('event.event', string='Events', copy=False)
    # active = fields.Boolean('Active', default=True)
    # is_default = fields.Boolean('Default question', help="Include by default in new events.")
    # is_reusable = fields.Boolean('Is Reusable',
                                #  compute='_compute_is_reusable', default=True, store=True,
                                #  help='Allow this question to be selected and reused for any future event. Always true for default questions.')
    #field_answer_ids = fields.One2many('field.question.answer', 'field_question_id', "Answers", copy=True)
    # sequence = fields.Integer(default=10)
    # is_mandatory_answer = fields.Boolean('Mandatory Answer')



