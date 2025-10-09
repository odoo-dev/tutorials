from odoo import models, fields


class EventEvent(models.Model):
    _inherit = "event.event"

    field_question_id = fields.Many2many("field.question", string="Field", copy=True)
    