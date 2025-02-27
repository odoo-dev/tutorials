from odoo import api, fields, models
from dateutil.relativedelta import relativedelta
from datetime import date


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    warranty_id = fields.Many2one('product.warranty.config', string="Warranty")
    end_date = fields.Date(string="End Date", compute='_compute_end_date', store=True)

    @api.depends('warranty_id')
    def _compute_end_date(self):
        for line in self:
            if line.warranty_id:
                line.end_date = date.today() + relativedelta(years=3)
            else:
                line.end_date = False

    @api.onchange('product_id')
    def _onchange_product_add_warranty(self):
        if self.product_id.is_warranty:
            warranty = self.env['product.warranty.config'].search(['product_tmpl_id', '=', self.product_id.id], limit=1)
            if warranty:
                self.warranty_id = warranty.id
                self.price_unit = self.product_id.list_price * (warranty.percentage / 100)
