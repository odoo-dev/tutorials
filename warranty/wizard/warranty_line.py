from odoo import api,fields,models
class WarrantyLine(models.TransientModel):
    _name = 'warranty.line'
    wizard_id = fields.Many2one('add.warranty.wizard')
    warranty_id = fields.Many2one('warranty.configuration')
    product_id = fields.Many2one(reated='warranty_id.product_id',string="Product")
    year = fields.Integer(related='warranty_id.year', string="year")
    end_date = fields.Date(string="End Date", compute='_compute_end_date', store=True)

    @api.depends('year')
    def _compute_end_date(self):
        for record in self:
            if record.year:
                record.end_date = date.today() + relativedelta(year=record.year)
                