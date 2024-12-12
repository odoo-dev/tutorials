from odoo import fields, models,api
from odoo.exceptions import UserError

class BudgetLines(models.Model):
    _name = "budget.budget.lines"
    _description = "Budget Line"

    budget_id = fields.Many2one('budget.budget', 'Budget', ondelete='cascade', index=True, required=True)
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.company.currency_id)
    analytic_line_ids = fields.One2many('account.analytic.line', 'budget_line_id', string='Analytic Lines')
    planned_amount = fields.Monetary(
        'Budget Amount', required=True,
        default=0.0,
        help="Amount you plan to earn/spend. Record a positive amount if it is a revenue and a negative amount if it is a cost.")
    practical_amount = fields.Monetary(string='Achieved Amount', compute='_compute_practical_amount', store=True)
    percentage = fields.Float(default=0.0,
        help="Comparison between practical and planned amount. This measure tells you if you are below or over budget.")

    @api.model_create_multi
    def create(self, vals_list):
        active_budget = None
        if self.env.context.get("active_id"):
            active_budget = self.env["budget.budget"].browse(self.env.context.get("active_id"))
            if active_budget.state != "draft":
                raise UserError("Budget lines can only be created when the state is 'draft'.")
        else:
            for vals in vals_list:
                budget_id = vals.get("budget_id")
                if budget_id:
                    active_budget = self.env["budget.budget"].browse(budget_id)
                    break
        
        if not active_budget:
            raise UserError("No budget found in context or record.")

        if active_budget.state != "draft":
            raise UserError("Budget lines can only be created when the state is 'draft'.")

        return super().create(vals_list)
    
    @api.depends("analytic_line_ids.amount")
    def _compute_practical_amount(self):
        for record in self:
            record.practical_amount = sum(record.analytic_line_ids.mapped("amount"))
            record.percentage = (
                (record.practical_amount / record.planned_amount) * 100
                if record.planned_amount > 0
                else 0.0
            )
            if (
                record.budget_id.on_over_budget == "warning"
                and record.practical_amount > record.planned_amount
            ):
                print("Achieved amount is more than your budget!")
                return True