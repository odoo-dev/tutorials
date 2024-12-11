from odoo import fields,models,api

class Budget(models.Model):
    _name="budget.budget"
    _description="Budget management"
    name = fields.Char(compute="_compute_name", store=True , string="Budget name")
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    state=fields.Selection([('draft' , 'Draft'),
                           ('confirmed' , 'Confirmed'),
                           ('revised' , 'Revised'),
                           ('done' , 'Done')
    ])
    responsible_id=fields.Many2one('res.users', string="Responsible")
    revision_id=fields.Many2one('res.users', string="Revision") 
    user_id=fields.Many2one('res.users' ,string="User Id")
    company=fields.Many2one('res.company', string='Company')
    budget_line_ids=fields.One2many('budget.line','budget_id', string="Budget Line Ids")
    color=fields.Integer(string='Color Index')

    @api.depends('start_date', 'end_date')
    def _compute_name(self):
        for record in self:
            if record.start_date and record.end_date:
                record.name = f"Budget : {record.start_date.strftime('%d/%m/%Y')} to {record.end_date.strftime('%d/%m/%Y')}"
            else:
                record.name = "Budget"
                