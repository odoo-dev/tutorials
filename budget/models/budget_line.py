from odoo import api, fields, models
from odoo.exceptions import ValidationError


class BudgetLine(models.Model):
    _name = "budget.line"
    _description = "Budget Line"

    analytic_acount_id = fields.Many2one("account.analytic.account", string="Analytic Account", store=True)
    budget_amount = fields.Integer(string="Budget Amount")
    achieved_amount = fields.Integer(string="Achieved Amount", compute="_compute_achieved_amount", store=True)
    achieved_percentage = fields.Integer(string="Achieved(%)", compute="_compute_achieved_percentage", store=True)
    budget_id = fields.Many2one("budget.budget", string="Budget")
    period_start_date = fields.Date(related="budget_id.period_start_date")
    period_end_date = fields.Date(related="budget_id.period_end_date")
    on_over_budget = fields.Selection(related="budget_id.on_over_budget")
    account_analytic_line_ids = fields.One2many("account.analytic.line", "budget_line_id", string="Account Analytic Lines")


    @api.constrains("budget_amount", "achieved_amount")
    def _check_budget_amount(self):
            for line in self:
                if line.achieved_amount > line.budget_amount and line.budget_id.on_over_budget == "restriction":
                    raise ValidationError("not allowed to create accont analytic line")
    @api.depends("achieved_amount", "budget_amount")
    def _compute_achieved_percentage(self):
        for line in self:
            line.achieved_percentage = line.budget_amount and 100*line.achieved_amount / line.budget_amount


    @api.depends("account_analytic_line_ids")
    def _compute_achieved_amount(self):
        for line in self:
            line.achieved_amount = sum(
                an_line.amount
                for an_line in line.account_analytic_line_ids
                if line.budget_id.period_start_date <= an_line.date <= line.budget_id.period_end_date
            )
        
    
    def open_account_analytic_view(self):
        return {    
            "type": "ir.actions.act_window",
            "res_model": "account.analytic.line",
            "view_mode": "list",
            "name": "Budget",
            "target": "new",
            "context": {
                "default_account_id": self.analytic_acount_id.id,
                "default_budget_line_id": self.id,
            },
            "domain": [
                ("account_id", "=", self.analytic_acount_id.id),
                ("budget_line_id", "=", self.id),
                ("date", ">=", self.budget_id.period_start_date),
                ("date", "<=", self.budget_id.period_end_date),
            ],
        }