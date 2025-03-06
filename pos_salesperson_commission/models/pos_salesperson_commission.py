from odoo import models, fields, api

class PosSalespersonCommission(models.Model):
    _name = 'pos.salesperson.commission'
    _description = 'POS Salesperson Commission'

    user_id = fields.Many2one('res.user_ids', string='Salesperson')
    order_ids = fields.One2many('pos.order', "salesperson_id", string='Orders')
   
    # commission = fields.a(compute='_compute_commission', store=True)

    # @api.depends('order_ids')
    # def _compute_commission(self):
    #     for record in self:
    #         total_sales = sum(order.amount_total for order in record.order_ids)
    #         record.commission = total_sales * 0.05  # 5% commission example