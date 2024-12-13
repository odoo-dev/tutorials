from odoo import fields, models,api
from odoo.exceptions import UserError,ValidationError

class BudgetLines(models.Model):
    _name = "budget.budget.lines"
    _description = "Budget Line"
    budget_id = fields.Many2one('budget.budget', 'Budget', ondelete='cascade', index=True, required=True)
    state = fields.Selection(related="budget_id.state", readonly=True)
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.company.currency_id)
    planned_amount = fields.Monetary(
        'Budget Amount', required=True,
        default=0.0,
        help="Amount you plan to earn/spend. Record a positive amount if it is a revenue and a negative amount if it is a cost.")
    practical_amount = fields.Monetary(string='Achieved Amount', compute='_compute_practical_amount',default=0.0, store=True)
    over_budget = fields.Monetary(
        string="Over Budget",
        default=0.0,
        compute="_compute_practical_amount",
        help="The amount by which the budget line exceeds its allocated budget.",
        store=True
    )
    count= fields.Integer('Count',computed="_compute_practical_amount",default=0, readonly=True)
    percentage = fields.Float(default=0.0,
        help="Comparison between practical and planned amount. This measure tells you if you are below or over budget.")

    def unlink(self):
        for record in self:
            if record.budget_id.state != "draft":
                raise UserError("You can only delete budget lines from draft state.")
        return super().unlink()
        
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
    
    @api.constrains("planned_amount")
    def _check_planned_amount(self):
        for record in self:
            if record.planned_amount < 0:
                raise ValidationError("Budget amount cannot be negative.")
    
    @api.depends("planned_amount","analytic_account_id")
    def _compute_practical_amount(self):
        for record in self:
            if not record.analytic_account_id:
                continue

            analytic_account_lines = self.env["account.analytic.line"].search_read(
                [
                    ("auto_account_id", "=", record.analytic_account_id.id),
                    ("date", ">=", record.budget_id.date_from),
                    ("date", "<=", record.budget_id.date_to),
                    ("amount", "<", 0),
                ],
                fields=["amount"],
            )

            achieved = sum(line.get("amount") for line in analytic_account_lines) or 0
            record.count = sum(1 for _ in analytic_account_lines) or 0
            record.practical_amount = abs(achieved)
            record.percentage = (
                (record.practical_amount / record.planned_amount) * 100
                if record.planned_amount > 0
                else 0.0
            )
            record.over_budget = max(0.0, record.practical_amount - record.planned_amount)
    
    def action_view_analytic_lines(self):
        if not self.budget_id:
            raise UserError("No budget linked to this budget line.")

        budget_start_date = self.budget_id.date_from
        budget_end_date = self.budget_id.date_to

        return {
            "type": "ir.actions.act_window",
            "name": "Analytic Lines",
            "res_model": "account.analytic.line",
            "view_mode": "list",
            "target": "current",
            "context": {
                "default_account_id": self.analytic_account_id.id,
                "budget_start_date": budget_start_date,
                "budget_end_date": budget_end_date,
            },
            "domain": [
                ("account_id", "=", self.analytic_account_id.id),
                ("date", ">=", budget_start_date),
                ("date", "<=", budget_end_date),
                ("amount", "<", 0),
            ],
        }