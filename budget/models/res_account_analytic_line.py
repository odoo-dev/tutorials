from odoo import models, fields, api
from odoo.exceptions import ValidationError

class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            entry_date = vals.get("date")
            if not entry_date:
                raise ValidationError("The date field is required to determine the appropriate budget.")
            
            budget_line = self.env["budget.budget.lines"].search([
                ("budget_id.date_from", "<=", entry_date),
                ("budget_id.date_to", ">=", entry_date),
                ("budget_id.active", "=", True),
                ("analytic_account_id", "=", vals.get("account_id"))
            ], limit=1)

            if budget_line:
                budget = budget_line.budget_id

                analytic_account_lines = self.env["account.analytic.line"].search_read(
                    [
                        ("account_id", "=", vals.get("account_id")),
                        ("date", ">=", budget.date_from),
                        ("date", "<=", budget.date_to),
                        ("amount", "<", 0),
                    ],
                    fields=["amount"],
                )
                achieved = (sum(line.get("amount") for line in analytic_account_lines))                
                calculated_achieved_amount = abs(achieved + vals.get("amount"))

                budget_line.over_budget = max(0.0, calculated_achieved_amount- budget_line.planned_amount)
                if budget.on_over_budget == "restriction":
                    if calculated_achieved_amount > budget_line.planned_amount:
                        raise ValidationError(
                            "You cannot create a budget line because it exceeds the allowed budget!"
                        )
                budget_line.practical_amount = calculated_achieved_amount
                budget_line.percentage = (
                    (calculated_achieved_amount / budget_line.planned_amount) * 100
                    if budget_line.planned_amount > 0
                    else 0.0
                )
        return super().create(vals_list)
    
    def write(self, vals):
        if "date" in vals or "amount" in vals or "account_id" in vals:
            for record in self:
                entry_date = vals.get("date", record.date)

                budget_line = self.env["budget.budget.lines"].search([
                    ("budget_id.date_from", "<=", entry_date),
                    ("budget_id.date_to", ">=", entry_date),
                    ("budget_id.active", "=", True),
                    ("analytic_account_id", "=", vals.get("account_id", record.account_id.id))
                ], limit=1)

                if budget_line:
                    budget = budget_line.budget_id

                    analytic_account_lines = self.env["account.analytic.line"].search_read(
                        [
                            ("account_id", "=", vals.get("account_id", record.account_id.id)),
                            ("date", ">=", budget.date_from),
                            ("date", "<=", budget.date_to),
                            ("amount", "<", 0),
                        ],
                        fields=["amount"],
                    )
                    achieved = (sum(line.get("amount") for line in analytic_account_lines))

                    new_amount = vals.get("amount", record.amount)
                    if budget.on_over_budget == "restriction":
                        if abs(achieved - record.amount + new_amount) > budget_line.planned_amount:
                            raise ValidationError(
                                "You cannot modify the budget line because it exceeds the allowed budget!"
                            )

        return super().write(vals)