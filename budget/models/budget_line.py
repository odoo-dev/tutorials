from odoo import fields, models
class BudgetLine(models.Model):
    _name="budget.line"
    _description="budeget lines"
    budget_id=fields.Many2one(comodel_name="budget.budget", string="Budget Id")
    budget_amount=fields.Float()
    achieved_amount=fields.Float()
    
