from odoo import fields, models
from odoo.exceptions import UserError
class BudgetLine(models.Model):
    _name="budget.line"
    _description="budeget lines"
    budget_line_name=fields.Char(string="Budget")
    budget_id=fields.Many2one(comodel_name="budget.budget", string="Budget Id")
    analytic_account_id=fields.Many2one('account.analytic.account', string="Analytic Account")    
    budget_amount=fields.Float()
    achieved_amount=fields.Float()
    over_budget = fields.Monetary(
        string="Over Budget",
        compute="_compute_achieved_amount",
        store=True,
        help="The amount by which the budget line exceeds its allocated budget.",
        currency_field="currency_id",
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
    )

    def _compute_achieved_amount(self):
        for record in self:
            if record.budget_amount:
                record.over_budget = record.achieved_amount - record.budget_amount

    def check_budget_warning(self):
        for record in self:
            if record.achieved_amount > record.budget_amount:
                raise UserError(
                    f"The achieved amount for '{record.budget_line_name}' exceeds the allocated budget. "
                    f"Please review the budget values."
                )
        
        return True 
        