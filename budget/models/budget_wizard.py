from odoo import fields, models


class BudgetWizard(models.TransientModel):
    _name = "budget.wizard"
    _decscription = "budget wizard"
    start_date = fields.Date()
    end_date = fields.Date()
    period = fields.Selection(
        [
            ("months", "Monthly"),
            ('quarter','Quarterly')
        ]
    )
