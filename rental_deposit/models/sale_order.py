# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create_multi(self, vals_list):
        orders = super().create(vals_list)
        for order in orders:
            order._add_deposit_line_if_needed()
        return orders

    def _add_deposit_line_if_needed(self):
        for line in self.order_line:
            product = line.product_id.product_tmpl_id
            if product.require_deposit and product.deposit_amount > 0:
                deposit_product_id = int(
                    self.env['ir.config_parameter'].sudo().get_param('rental_deposit.deposit_product_id', default=0)
                )
                if not deposit_product_id:
                    continue  

                if any(l.product_id.id == deposit_product_id for l in self.order_line):
                    continue

                self.order_line.create({
                    'order_id': self.id,
                    'product_id': deposit_product_id,
                    'price_unit': product.deposit_amount,
                    'product_uom_qty': 1,
                    'name': 'Deposit for ' + product.name,
                })