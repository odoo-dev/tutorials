# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models


class SaleOrderWizard(models.TransientModel):
    _name = 'sale.order.wizard'
    _description = 'Sale Order Wizard'

    sale_order_wizard_line_id = fields.One2many(
        'sale.order.line.wizard', 'sales_order_wizard_ids', string="Sale Order Lines")

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        order_line_id = self.env.context.get('active_id')
        if order_line_id:
            order_data = self.env['sale.order.line'].browse(
                order_line_id).order_id
            
            dividend = len(order_data.order_line)
            line_wizard_data = []
            for order in order_data.order_line:
                line_wizard_data.append((0, 0, {
                    'name': order.name,
                    'price': order.price_subtotal / dividend
                }))
                print(line_wizard_data,'line_wizard_data')
                defaults['sale_order_wizard_line_id'] = line_wizard_data

        return defaults
