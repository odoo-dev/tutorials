from odoo import fields, models


class DentalChronicConditions(models.Model):
    _name = "dental.chronic.conditions"
    _description = "Table contains patient chronic condition details."

    name = fields.Char()
    sequence = fields.Integer("Sequence")