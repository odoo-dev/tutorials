# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrderWizard(models.TransientModel):
    _name = 'sale.order.wizard'
    _description = 'Sale Order Wizard'

    original_price = fields.Float('Original Price')
    original_total_price = fields.Float('Original Total Price')
    sale_order_wizard_line_id = fields.One2many(
        'sale.order.line.wizard', 'sales_order_wizard_ids', string="Sale Order Lines")

    @api.model
    def default_get(self, fields_list):
        defaults = super(SaleOrderWizard, self).default_get(fields_list)
        order_line_id = self.env.context.get('active_id')
        if order_line_id:
            order_line_data = self.env['sale.order.line'].browse(
                order_line_id)
            sale_order_data = order_line_data.order_id
            if len(sale_order_data.order_line) > 1:
                dividend_price = order_line_data.price_subtotal / \
                    (len(sale_order_data.order_line)-1)
                line_wizard_data = []
                for order in sale_order_data.order_line:
                    if order.id != order_line_id:
                        line_wizard_data.append((0, 0, {
                            'name': order.name,
                            'price': order.price_subtotal + dividend_price,
                            'sale_order_line_id': order.id
                        }))
                defaults['original_total_price'] = sale_order_data.amount_untaxed
                defaults['original_price'] = order_line_data.price_subtotal
                defaults['sale_order_wizard_line_id'] = line_wizard_data
        return defaults

    def calculate_divident(self):
        for record in self:
            total_sum = sum(record.sale_order_wizard_line_id.mapped('price'))
            if total_sum > record.original_total_price:
                raise ValidationError(
                    _('Sum of total of updated amount should not be greater than the previous total amount.'))
            for data in record.sale_order_wizard_line_id:
                sale_order_line = self.env['sale.order.line'].browse(
                    data.sale_order_line_id.id)
                sale_order_line.computed_price_ids = [(6, 0, [data.id])]
