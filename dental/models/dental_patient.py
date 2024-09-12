from odoo import models, fields, Command, api


class DentalPatients(models.Model):

    _name = "dental.patient"
    _description = "Dental patient"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string='Name', required=True)
    image = fields.Image()

    stage_id = fields.Many2one('dental.stage', string="Stage",
                               default=lambda self: self.env.ref('dental.stage_1').id)
    gp_id = fields.Many2one('res.partner', string="GP's Name")
    gp_phone = fields.Char(related='gp_id.phone')
    chronic_condition_ids = fields.Many2many(
        'dental.chronic.condition', string='Chronic Conditions')
    allergie_ids = fields.Many2many('dental.allergy', string='Allergies')
    substance_abuse_ids = fields.Many2many(
        'dental.habit', string='Habits/Substance Abuse')
    hospitalized_this_year = fields.Char(string='Hospitalized this Year')
    medication = fields.Many2many('dental.medication', string='Medication')
    under_specialist_care = fields.Char(string='Under Specialist Care')
    psychiatric_history = fields.Char(string='Psychiatric History')
    pregnant = fields.Boolean(string='Are you pregnant?')
    nursing = fields.Boolean(string='Are you nursing?')
    hormone_treatment = fields.Selection([
        ('hrt', 'Hormone Replacement Treatment'),
        ('birth_control', 'Birth Control'),
        ('neither', 'Neither')
    ], string='Hormone Treatment')

    # Medical Aid Details
    medical_aid_id = fields.Many2one(
        'dental.medical.aids', string='Medical Aid')
    medical_aid_plan = fields.Char(string='Medical Aid Plan')
    medical_aid_number = fields.Char(string='Medical Aid Number')
    main_member_code = fields.Char(string='Main Member Code')
    dependant_code = fields.Char(string='Dependant Code')
    notes = fields.Text()

    # Basic patient details
    ocuupation = fields.Char(string='Patient occupation')
    date_of_birth = fields.Date(string='Date of Birth')
    identity_number = fields.Char(string='Identity Number')
    gender = fields.Selection(string='Gender',
                              selection=[
                                  ('male', 'Male'),
                                  ('female', 'Female'),
                                  ('neither', 'Neither')
                              ], default='neither'
                              )
    marital_status = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('widowed', 'Widowed'),
        ('divorced', 'Divorced')
    ], string='Marital Status')

    # Related fields for Contacts
    emergency_contact_id = fields.Many2one(
        'res.partner', string='Emergency Contact')
    emergency_phone = fields.Char(
        string='Phone no.', related='emergency_contact_id.phone')
    company_id = fields.Many2one(
        'res.partner', string='Company or School', default=lambda self: self.env.company)

    consent_signature = fields.Binary(string="Consent Signature")
    consent_date = fields.Date(string="Consent Date")

    # Guarantor fields
    guarantor_id = fields.Many2one('res.users', string='Guarantor')
    guarantor_mobile = fields.Char(
        related='guarantor_id.mobile', string='Guarantor Mobile Phone')
    guarantor_phone = fields.Char(related='guarantor_id.phone', string='Phone')
    guarantor_email = fields.Char(related='guarantor_id.email', string='Email')
    guarantor_company_id = fields.Many2one(
        'res.company', string='Company or School', default=lambda self: self.env.company)

    history_ids = fields.One2many('dental.medical.history', 'patient_id')

    def action_create_invoice(self):
        move_vals = {
            'partner_id': self.guarantor_id.id,
            'move_type': 'out_invoice',
            'invoice_date': fields.Date.today(),
            "invoice_line_ids": [
                Command.create({
                    "name": "consultant fees",
                    "quantity": 1,
                    "price_unit": 1000,
                }),
            ],

        }
        self.env['account.move'].create(move_vals)
        self.stage_id = self.env.ref('dental.stage_3').id

    def action_book_appointment(self):
        vals = {
            'name': f"{self.name}-Dentist Booking",
            'appointment_type_id': self.env.ref('appointment.appointment_type_dental_care').id,
            'duration': 0.5
        }
        self.env['calendar.event'].create(vals)
        self.stage_id = self.env.ref('dental.stage_4').id

    @api.model
    def create(self, vals):
        obj = super().create(vals)
        self.env['dental.medical.history'].create({
            'date': fields.Date.today(),
            'patient_id': obj.id,
            'did_not_attend': True
        })
        existing_patients = obj.search(
            [('name', '=', obj.name), ('id', '!=', obj.id)])
        if existing_patients:
            obj.history_ids += existing_patients.history_ids
        return obj
