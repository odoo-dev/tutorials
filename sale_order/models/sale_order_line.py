# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models


class SaleOrderLine(models.Model):
    _inherit = ['sale.order.line']

    divided_price = fields.Float("Divided Price")
    sale_tag_line_id = fields.Many2many('sale.order.line.tag', string='Tag')
