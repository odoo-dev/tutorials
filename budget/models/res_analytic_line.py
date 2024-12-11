from odoo import fields,models

class AnalyticLineBudget(models.Model):
    _inherit = "account.analytic.line"

    budget_line_id = fields.Many2one('budget.budget.lines', string='Budget Line')
