from odoo import fields,models,api
from odoo.exceptions import ValidationError
class AnalyticLineBudget(models.Model):
    _inherit = "account.analytic.line"

    budget_line_id = fields.Many2one('budget.budget.lines', string='Budget Line')
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            budget_line = self.env["budget.budget.lines"].browse(
                vals.get("budget_line_id")
            )
            budget = budget_line.budget_id
            if budget.on_over_budget == "restriction":
                if sum(budget_line.analytic_line_ids.mapped("amount"))+ vals.get("amount") > budget_line.planned_amount:
                    raise ValidationError(
                        "You cannot create a budget line because it exceeds the allowed budget!"
                    )
        return super().create(vals_list)

