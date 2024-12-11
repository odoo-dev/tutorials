from odoo import models, fields
from odoo.exceptions import ValidationError
from datetime import timedelta
from dateutil.relativedelta import relativedelta

class BudgetWizard(models.TransientModel):
    _name = "budget.wizard"

    date_from = fields.Date(required=True, string="Start Date")
    date_to = fields.Date(
        string="Expiration Date",
        required=True,
        index=True,
    )
    periods = fields.Selection(
        selection=[("monthly", "Monthly"), ("quarterly", "Quarterly")],
        required=True,
        default="monthly",
    )
    # analytic_account_ids = fields.Many2many('account.analytic.account', 'Analytic Accounts')

    def action_add_budget(self):
        if self.date_from >= self.date_to:
            raise ValidationError("Start Date must be before Expiration Date.")

        current_date = self.date_from
        budget_entries = []

        while current_date <= self.date_to:
            # Calculate the last day of the current month
            end_of_month = current_date + relativedelta(day=31)

            # Determine actual end date for this budget entry
            if end_of_month > self.date_to:
                end_of_month = self.date_to

            # Create budget entry from current_date to end_of_month
            budget_entries.append(
                {
                    "name": f"Budget from {current_date.strftime('%d-%m-%Y')} to {end_of_month.strftime('%d-%m-%Y')}",
                    "date_from": current_date,
                    "date_to": end_of_month,
                }
            )

            # Move to the first day of the next month
            current_date = end_of_month + timedelta(days=1)

            if current_date > self.date_to:
                break

        self.env["budget.budget"].create(budget_entries)

        return {"type": "ir.actions.act_window_close"}