# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, fields, models


class SaleOrderLineWizard(models.TransientModel):
    _name = 'sale.order.line.wizard'
    _description = 'Sale Order Wizard'

    name = fields.Char('Name')
    price = fields.Float('Price',precision_rounding=2)
    sales_order_wizard_ids = fields.Many2one(
        'sale.order.wizard', string='Sale Order Line')
    sale_order_line_id = fields.Many2one(
        'sale.order.line', string='Related Sale Order Line')