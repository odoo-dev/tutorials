from odoo import models, fields


class EventType(models.Model):
    _inherit = "event.type"

    field_question_id = fields.Many2many("field.question", string="Field", copy=True)
    partner_question_ids = fields.Many2many("partner.question")