from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError


class BudgetLine(models.Model):
    _name = "budget.budget.lines"
    _description = "budeget lines"
    name = fields.Char(string="Budget")
    budget_id = fields.Many2one(
        comodel_name="budget.budget", 
        required=True, 
        string="Budget Id"
    )
    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account", 
        string="Analytic Account"
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
    )
    budget_amount = fields.Monetary(
        string="Budget Amount",
        default=0.0,
        currency_field="currency_id",
        help="The total allocated budget for this budget line.",
    )
    achieved_amount = fields.Monetary(
        string="Achieved Amount",
        compute="_compute_achieved_amount",
        currency_field="currency_id",
        store=True
    )
    over_budget = fields.Monetary(
        string="Over Budget",
        compute="_compute_achieved_percentage_and_over_budget",
        store=True,
        currency_field="currency_id",
    )

    achieved_percentage = fields.Float(
        string="Achieved (%)",
        compute="_compute_achieved_percentage_and_over_budget",
        readonly=True,
        store=True,
    )
    state = fields.Selection(related="budget_id.state", store=True)
    count_account_analytic_line = fields.Integer()
    user_id = fields.Many2one(related="budget_id.responsible_id")
    start_date = fields.Date(related="budget_id.start_date")
    end_date = fields.Date(related="budget_id.end_date")

    @api.depends("budget_amount")
    def _compute_achieved_amount(self):
        
        for record in self:
        
            if not record.analytic_account_id:
                record.achieved_amount = 0.0
                record.achieved_percentage = 0.0
                record.over_budget = 0.0
                continue
            

            analytic_account_lines = self.env["account.analytic.line"].search(
                [
                    ("auto_account_id", "=", record.analytic_account_id.id),
                    ("date", ">=", record.budget_id.start_date),
                    ("date", "<=", record.budget_id.end_date),
                    ("amount", "<", 0),  
                ]
            )

            achieved = sum(line.amount for line in analytic_account_lines)
            record.achieved_amount = abs(achieved)


    @api.depends("achieved_amount")
    def _compute_achieved_percentage_and_over_budget(self):
        # print("% " * 100)
        for record in self:
            if (
                record.analytic_account_id
                and record.budget_amount
                and record.achieved_amount
            ):
                record.achieved_percentage = (
                    (record.achieved_amount / record.budget_amount) * 100
                    if record.budget_amount > 0
                    else 0.0
                )
                record.over_budget = max(
                    0.0, record.achieved_amount - record.budget_amount
                )

    def check_budget_warning(self):
        for record in self:
            if record.achieved_amount > record.budget_amount:
                raise UserError(
                    f"The achieved amount for '{record.name}' exceeds the allocated budget. "
                    f"Please review the budget values."
                )
        return True

    @api.constrains("budget_amount")
    def _check_budget_amount(self):
        for record in self:
            if record.budget_amount < 0:
                raise ValidationError("Budget amount cannot be negative.")

    def action_open_analytic_lines(self):
        if not self.budget_id:
            raise UserError("No budget linked to this budget line.")

        budget_start_date = self.budget_id.start_date
        budget_end_date = self.budget_id.end_date

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

    @api.model_create_multi
    def create_budget_line(self, vals_list):
        for vals in vals_list:
            budget_id = vals.get("budget_id")

            budget = self.env["budget.budget"].browse(budget_id)

            if budget.state == "draft":
                raise UserError(
                    "Cannot create budget lines for a budget in the 'draft' stage."
                )
            return self.create(vals_list)
