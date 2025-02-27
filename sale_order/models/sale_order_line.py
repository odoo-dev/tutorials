# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = ['sale.order.line']

    computed_price_ids = fields.Many2many(
        'sale.order.line.wizard', string="Division")
