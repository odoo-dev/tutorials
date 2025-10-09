from odoo import fields, models, api
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = "res.partner"

    aadhar_number = fields.Char(string="Aadhar Number", size=12, required=True)
    passing_year = fields.Integer(string="Passing Year", required=True)
    course = fields.Char(string="Course")
    college = fields.Char(string="College")


    partner_answer_ids = fields.One2many('partner.answer','partner_id')
    @api.model
    def _get_frontend_writable_fields(self):
        fields = super()._get_frontend_writable_fields()
        fields.update({'aadhar_number', 'passing_year', 'course', 'college'})
        return fields


    field_answer_ids = fields.One2many(
        'field.registration.answer', 
        'partner_id', 
        string='Field Answers'
    )