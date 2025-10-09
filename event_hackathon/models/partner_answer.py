from odoo import models, fields


class PartnerAnswer(models.Model):
    _name = "partner.answer"


    question_id = fields.Many2one(
            'partner.question', ondelete='restrict', required=True,
            string='Question')
    partner_id = fields.Many2one('res.partner')
    value_text_box = fields.Text('Text answer')