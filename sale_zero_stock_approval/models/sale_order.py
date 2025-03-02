# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    zero_stock_approval = fields.Boolean(string='Approval', copy=False)

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super().fields_get(allfields, attributes)
        if not self.env.user.has_group('sales_team.group_sale_manager'):
            if 'zero_stock_approval' in res:
                res['zero_stock_approval']['readonly'] = True
        return res

    def action_confirm(self):
        orders_with_zero_stock = self.search([('zero_stock_approval', '=', False),('order_line.product_uom_qty', '<=', 0)])
        if orders_with_zero_stock:
            raise UserError(_('Cannot confirm order with zero stock products without approval.'))
        return super().action_confirm()
