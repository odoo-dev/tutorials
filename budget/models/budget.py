from odoo import models, fields, api
from odoo.exceptions import ValidationError
import ast

class Budget(models.Model):
    _name = "budget.budget"
    _inherit = ['mail.thread']
    _description = "Budget"

    name = fields.Char('Budget Name', required=True)
    color= fields.Integer(default=5)
    user_id = fields.Many2one('res.users', 'Responsible', default=lambda self: self.env.user)
    date_from = fields.Date('Start Date')
    date_to = fields.Date('End Date')
    revision_id = fields.Integer()
    is_favorite = fields.Boolean(default=False)
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('revised', 'Revised'),
        ('done', 'Done'),
    ], string='Status', default='draft', required=True, readonly=True, copy=False)

    on_over_budget = fields.Selection([
        ('warning', 'Show a warning'),
        ('restriction', 'Restrict on creation'),    
    ], string='Over Budget Policy')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.company.currency_id)
    budget_line = fields.One2many('budget.budget.lines', 'budget_id', 'Budget Lines', copy=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda self: self.env.company)
    achieved_amount = fields.Monetary(string='Achieved Amount', compute='_compute_achieved_amount', store=True)

    @api.depends('date_from', 'date_to')
    def _compute_name(self):
        for record in self:
            if not record.name and record.date_from and record.date_to:
                record.name = f"Budget {record.date_from} to {record.date_to}"

    @api.depends('budget_line.practical_amount')
    def _compute_achieved_amount(self):
        for record in self:
            record.achieved_amount = sum(line.practical_amount for line in record.budget_line)

    @api.constrains('date_from', 'date_to')
    def _check_date_difference(self):
        for record in self:
            if record.date_from == record.date_to:
                raise ValidationError("Start Date and End Date cannot be the same.")
    
    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for record in self:
            if record.date_to < record.date_from:
                raise ValidationError("End Date must be after Start Date.")

    def action_budget_confirm(self):
        if self.state != 'draft':
            raise ValidationError("Only budgets in draft state can be confirmed.")
        self.write({'state': 'confirmed'})

    def action_budget_revise(self):
        if self.state not in ['draft', 'confirmed']:
            raise ValidationError("Only budgets in draft or confirmed state can be revised.")
        self.write({'state': 'revised'})

    def action_budget_draft(self):
        if self.state not in ['confirmed', 'revised']:
            raise ValidationError("Only confirmed or revised budgets can be set back to draft.")
        self.write({'state': 'draft'})

    def action_budget_done(self):
        if self.state != 'revised':
            raise ValidationError("Only revised budgets can be marked as done.")
        self.write({'state': 'done'})
        
    # def action_open_budget_form(self):
    #     # return{
    #     #     'name':'Budget'
    #     #     'r'
    #     # }
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': _('Import your first bill'),
    #         'view_mode': 'form',
    #         'res_model': 'budget.budget',
    #         'views': 'form',
    #     }

    #     action = self.env['ir.actions.act_window']._for_xml_id('budget.budget_form_action')
    #     # action['display_name'] = _("%(name)s's Budget Form", name=self.name)
    #     action_context = ast.literal_eval(action['context']) if action['context'] else {}
    #     action_context['default_budget_id'] = self.id
    #     return dict(action, context=action_context)