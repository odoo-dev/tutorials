from odoo import models, fields, api

class PosSalespersonCommission(models.Model):
    _name = 'pos.salesperson.commission'
    _description = 'POS Salesperson Commission'

    user_id = fields.Many2one('res.users', string='Salesperson')
    order_ids = fields.One2many('pos.order', "commission_id", string='Orders')
   
    order_count = fields.Integer(string="Number of Orders", compute="_compute_order_count", store=True)
    total_commission = fields.Float(string="Total Commission", compute="_compute_total_commission", store=True)

    @api.depends('order_ids')
    def _compute_order_count(self):
        for record in self:
            record.order_count = len(record.order_ids)

    @api.depends('order_ids')
    def _compute_total_commission(self):
        for record in self:
            total_sales = sum(order.amount_total for order in record.order_ids)
            record.total_commission = total_sales * 0.05