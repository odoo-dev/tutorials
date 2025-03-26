# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    global_info_line_ids = fields.One2many(
        comodel_name='global.info.line',
        inverse_name='order_id',
        string="Global Info Lines",
    )

    product_category_id = fields.Integer(
        related='global_info_line_ids.product_category_id.id',
        string="Product Category",
    )

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        orders._generate_global_info_lines()
        return orders

    def _generate_global_info_lines(self):
        for order in self:
            product_categories = self.env['product.category'].search([('show_on_global_info', '=', True)])
            existing_lines = {
                (line.product_category_id.id, line.attribute_id.id): line.id 
                for line in order.global_info_line_ids
            }
            new_lines = [
                {'order_id': order.id, 'product_category_id': cat.id, 'attribute_id': attr.id}
                for cat in product_categories
                for attr in cat.default_attribute_ids
                if (cat.id, attr.id) not in existing_lines
            ]
            keep_line_ids = {existing_lines[key] for key in existing_lines if key in [(cat.id, attr.id) for cat in product_categories for attr in cat.default_attribute_ids]}
            unlink_line_ids = set(existing_lines.values()) - keep_line_ids
            if unlink_line_ids:
                self.env['global.info.line'].browse(list(unlink_line_ids)).unlink()
            if new_lines:
                self.env['global.info.line'].create(new_lines)
