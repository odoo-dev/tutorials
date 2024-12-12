from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError

class Budget(models.Model):
    _name = "budget.budget"
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
        
    )
    responsible_id = fields.Many2one("res.users", string="Responsible")
    revision_id = fields.Many2one("res.users", string="Revision")
    user_id = fields.Many2one("res.users", string="User Id")
    company_id = fields.Many2one("res.company", string="Company")
    budget_line_ids = fields.One2many(
        "budget.budget.lines", "budget_id", string="Budget Line Ids"
    )
    color = fields.Integer(string="Color Index")
    active_id=fields.Boolean()

    on_over_budget = fields.Selection(
        selection=[("warning", "Warning"), ("restriction", "Restriction")],
        
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

    def action_revise(self):
        for record in self:
            if record.state == "confirmed":
                record.revision_id = self.env.user
                record.state = "revised"
            else:
                raise UserError("Only confirmed budgets can be revised.")

    def action_done(self):
        for record in self:
            if record.state in ["confirmed", "revised"]:
                record.state = "done"

    @api.model
    def create_budget_line(self):
        for budget in self:
            # if not budget:
            #     raise UserError("The specified budget does not exist.")

            budget_line = self.env["budget.budget.lines"].create(
                {
                    "budget_id": budget.id,
                    "name": f"Budget Line for {budget.name}",
                    "analytic_account_id": None,  # Default or placeholder value
                    "budget_amount": 0.0,  # Default budget amount
                    "currency_id": budget.company_id.currency_id.id,
                }
            )

            return budget_line

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
