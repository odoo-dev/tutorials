from odoo import fields,models

class BudgetBudget(models.Model):
    _name="budget.budget"
    _description="Budget management"
    name=fields.Char(required=True)
    