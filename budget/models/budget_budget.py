from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError
from markupsafe import Markup


class Budget(models.Model):
    _name = "budget.budget"
    _inherit = ["mail.thread", "mail.activity.mixin"] 
    _description = "Budget management"
    name = fields.Char(compute="_compute_name", store=True, string="Budget name")
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("revised", "Revised"),
            ("done", "Done"),
        ],
        required=True,
        default="draft",
        tracking=True
    )
    responsible_id = fields.Many2one( "res.users", string="Responsible",  tracking=True)
    revision_id = fields.Many2one("res.users", string="Revision",tracking=True)
    user_id = fields.Many2one("res.users", string="User Id")
    company_id = fields.Many2one("res.company", string="Company")
    budget_line_ids = fields.One2many(
        "budget.budget.lines", "budget_id", string="Budget Line Ids"
    )
    color = fields.Integer(string="Color Index")
    active = fields.Boolean(string="Active", default=True)

    on_over_budget = fields.Selection(
        selection=[("warning", "Warning"), ("restriction", "Restriction")],
        tracking=True
    )
    warnings = fields.Text(compute="_action_over_budget")
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
    )

    @api.depends("start_date", "end_date")
    def _compute_name(self):
        for record in self:
            if record.start_date and record.end_date:
                record.name = f"Budget : {record.start_date.strftime('%d/%m/%Y')} to {record.end_date.strftime('%d/%m/%Y')}"
            else:
                record.name = "Budget"

    def action_reset_to_draft(self):
        for record in self:
            if record.state != "draft":
                record.state = "draft"

    def action_confirmed(self):
        for record in self:
            if record.state == "draft":
                record.state = "confirmed"            

    def action_done(self):
        for record in self:
            if record.state in ["confirmed", "revised"]:
                record.state = "done"

   
    @api.constrains("start_date", "end_date", "company_id")
    def _check_time_overlap(self):
        for budget in self:
            same_period_budget = self.env["budget.budget"].search([
                ("id", "!=", budget.id),  
                ("company_id", "=", budget.company_id.id), 
                "|",
                "&", ("start_date", "<=", budget.start_date), ("end_date", ">=", budget.start_date),
                "&", ("start_date", "<=", budget.end_date), ("end_date", ">=", budget.end_date),
            ])
            
            if same_period_budget:
                raise ValidationError(
                    "The budget period overlaps with an existing budget for the same company Please adjust the period."
                )

    def action_revise(self):
        for record in self:
            if record.state != "confirmed":
                raise UserError("Only confirmed budgets can be revised.")

            record.write({
                "revision_id": self.env.user.id,
                "state": "revised",
                "active": False,
            })

            new_budget = record.copy({"revision_id": None, "state": "draft", "active": True})


            budget_lines_vals = [
                {
                    "budget_id": new_budget.id,
                    "name": line.name,
                    "budget_amount": line.budget_amount,
                    "achieved_amount": line.achieved_amount,
                    "achieved_percentage": line.achieved_percentage,
                    "analytic_account_id": line.analytic_account_id.id,
                    "currency_id": line.currency_id.id,
                }
                for line in record.budget_line_ids
            ]
            self.env["budget.budget.lines"].create(budget_lines_vals)

            
            action = self.env.ref("budget.action_budgets_menu")
            record.message_post(
                body=Markup(
                        f'<a href="odoo/action-{action.id}/{new_budget.id}">{new_budget.name}</a>.'
                    )
            )

    @api.depends("budget_line_ids.over_budget")
    def _action_over_budget(self):
        for record in self:
            over_budget_exists = False
            for over_budget in record.budget_line_ids.mapped("over_budget"):
                print("*-*")
                print(over_budget)
                if  over_budget > 0:
                    over_budget_exists = True
                    break

            if record.on_over_budget == "warning" and over_budget_exists:
                record.warnings = "Achieved amount exceeds the budget!"
            else:
                record.warnings = False
        
