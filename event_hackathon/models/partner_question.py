from odoo import models, fields


class PartnerQuestion(models.Model):
    _name = "partner.question"

    title = fields.Char(string="Field Name", required=True, translate=True)
    event_type_ids = fields.Many2many('event.type', string='Event Types')