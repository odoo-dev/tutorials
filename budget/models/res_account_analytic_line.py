from odoo import models, api
from odoo.exceptions import ValidationError

class ResAccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            entry_date = vals.get("date")
            if not entry_date:
                raise ValidationError("The date field is required to determine the appropriate budget.")

            budget_line = self.env["budget.budget.lines"].search([
                ("budget_id.start_date", "<=", entry_date),
                ("budget_id.end_date", ">=", entry_date),
                ("budget_id.active", "=", True),
                ("analytic_account_id", "=", vals.get("account_id"))
            ], limit=1)

            if budget_line:
                budget = budget_line.budget_id
                analytic_account_lines = self.env["account.analytic.line"].search([
                    ("account_id", "=", vals.get("account_id")),
                    ("date", ">=", budget.start_date),
                    ("date", "<=", budget.end_date),
                    ("amount", "<", 0),
                ])

                achieved = sum(line.amount for line in analytic_account_lines)

        
                if budget.on_over_budget == "restriction" and abs(achieved + vals.get("amount")) > budget_line.budget_amount:
                    raise ValidationError(
                        "You cannot create a budget line because it exceeds the allowed budget!"
                    )
                    
                budget_line.achieved_amount = abs(achieved + vals.get("amount"))
                budget_line.count_account_analytic_line = len(analytic_account_lines) + 1    

        return super().create(vals_list)


    def write(self, vals):
        if any(field in vals for field in ["date", "amount", "account_id"]):
            for record in self:
              
                entry_date = vals.get("date", record.date)
                account_id = vals.get("account_id", record.account_id.id)

                
                budget_line = self.env["budget.budget.lines"].search([
                    ("budget_id.start_date", "<=", entry_date),
                    ("budget_id.end_date", ">=", entry_date),
                    ("budget_id.active", "=", True),
                    ("analytic_account_id", "=", account_id)
                ], limit=1)

                if budget_line:
                    budget = budget_line.budget_id

                    achieved = sum(line.amount for line in self.env["account.analytic.line"].search([
                        ("account_id", "=", account_id),
                        ("date", ">=", budget.start_date),
                        ("date", "<=", budget.end_date),
                        ("amount", "<", 0),
                    ]))

                    new_amount = vals.get("amount", record.amount)
                    if budget.on_over_budget == "restriction" and abs(achieved - record.amount + new_amount) > budget_line.budget_amount:
                        raise ValidationError(
                            "You cannot modify the budget line because it exceeds the allowed budget!"
                        )

        return super().write(vals)

