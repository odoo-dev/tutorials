from odoo import models, Command, fields
from dateutil.relativedelta import relativedelta
from datetime import timedelta
from datetime import date


class BudgetWizard(models.TransientModel):
    _name = "budget.wizard"
    _decscription = "budget wizard"
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    period = fields.Selection([("months", "Monthly"), ("quarter", "Quarterly")], required=True)
    analytical_account_ids=fields.Many2many(comodel_name='account.analytic.account')
    

    def action_create_multiple_budgets(self):
        Budget = self.env["budget.budget"]
        user = self.env.user

        if self.start_date >= self.end_date:
            raise ValueError("Start Date must be before End Date.")

        current_date = self.start_date
        budget_entries = []

        while current_date <= self.end_date:
            if self.period == "months":
                next_date = current_date + relativedelta(months=1)
            elif self.period == "quarter":
                next_date = current_date + relativedelta(months=3)
            else:
                break 

            end_date = min(next_date - timedelta(days=1), self.end_date)

            budget_entries.append({
                "name": (
                    f"Budget - {current_date.strftime('%B-%Y')}"
                    if self.period == "months"
                    else f"Budget - {current_date.strftime('%d %B, %Y')} to {end_date.strftime('%d %B, %Y')}"
                ),
                "start_date": current_date,
                "end_date": end_date,
                "user_id": user.id,
                "company_id": self.env.company.id,
                "budget_line_ids": [
                    Command.create({
                        "name": "budget line", 
                        "analytic_account_id": account.id
                    }) for account in self.analytical_account_ids
                ]
            })
            print("*-*"*100)
            print(self.id)

            current_date = next_date

        Budget.create(budget_entries)

        return {
            "type": "ir.actions.client",
            "tag": "reload",
            "message": "Budgets have been successfully created."
        }
