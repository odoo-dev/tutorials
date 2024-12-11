from odoo import fields, models
from dateutil.relativedelta import relativedelta
from datetime import date


class BudgetWizard(models.TransientModel):
    _name = "budget.wizard"
    _decscription = "budget wizard"
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    period = fields.Selection([("months", "Monthly"), ("quarter", "Quarterly")], required=True)

    def action_create_budgets(self):
        Budget = self.env["budget.budget"]
        user = self.env.user

        current_date = self.start_date
        while current_date <= self.end_date:
            if self.period == "months":
                next_date = current_date + relativedelta(months=1)
            elif self.period == "quarter":
                quarter = (current_date.month - 1) // 3 + 1
                next_date = current_date + relativedelta(months=3)
            else:
                break
            Budget.create({
                'start_date': current_date,
                'end_date': next_date - relativedelta(days=1),
                'user_id': user.id,
            })
            current_date = next_date
         