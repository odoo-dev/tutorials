from odoo import fields, models,api
from odoo.exceptions import UserError
# from collections import defaultdict
# from datetime import timedelta
# from odoo.osv.expression import AND

class BudgetLines(models.Model):
    _name = "budget.budget.lines"
    _description = "Budget Line"

    name = fields.Char()
    budget_id = fields.Many2one('budget.budget', 'Budget', ondelete='cascade', index=True, required=True)
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.company.currency_id)
    analytic_line_ids = fields.One2many('account.analytic.line', 'budget_line_id', string='Analytic Lines')
    
    planned_amount = fields.Monetary(
        'Budget Amount', required=True,
        help="Amount you plan to earn/spend. Record a positive amount if it is a revenue and a negative amount if it is a cost.")
    
    practical_amount = fields.Monetary(defaultstring='Achieved Amount', help="Amount really earned/spent.")
    
    percentage = fields.Float(default=3,
        help="Comparison between practical and planned amount. This measure tells you if you are below or over budget.")

    @api.model
    def create(self, vals):
        budget = self.env['budget.budget'].browse(vals.get('budget_id'))
        # breakpoint()
        if budget:
            # Check if achieved amount exceeds planned amount
            if budget.on_over_budget == 'warning' and budget.achieved_amount > sum(line.planned_amount for line in budget.budget_line):
                # Display warning message
                warning_msg = "Warning: Achieved amount exceeds planned budget."
                self.env.user.notify_info(warning_msg)
            elif budget.on_over_budget == 'restriction' and budget.archived_amount > sum(line.planned_amount for line in budget.budget_line):
                raise UserError("Cannot create account analytic line: Achieved amount exceeds planned budget.")
        
        return super(BudgetLines, self).create(vals)
