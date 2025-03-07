from odoo import api, models, fields
# from odoo.exceptions import User


class PosOrder(models.Model):
    _inherit = 'pos.order'

    salesperson_id = fields.Many2one('res.users', string='Salesperson', help="Salesperson associated with the order")
    commission_id = fields.Many2one('pos.salesperson.commission', string='Commission')
    commission_amount = fields.Float(string="Commission Amount", compute="_compute_commission_amount")
    
    def _process_commission_lines(self, pos_order):
        if pos_order.salesperson_id:
            existing_commission = self.env["pos.salesperson.commission"].search([("user_id", "=", pos_order.salesperson_id.id)])
            if existing_commission:
                existing_commission.write({'order_ids': [(4, pos_order.id)]})
            else:
                self.env["pos.salesperson.commission"].create({
                    "user_id": pos_order.salesperson_id.id,
                    "order_ids": [(4, pos_order.id)],
                })
        return pos_order
    
    @api.depends('amount_total')
    def _compute_commission_amount(self):
        for order in self:
            order.commission_amount = order.amount_total * 0.05