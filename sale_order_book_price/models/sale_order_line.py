# -*- coding: utf-8 -*-

from odoo import models, fields, api


class sale_order_line(models.Model):
    _name = 'sale.order.line'
    _inherit = 'sale.order.line'
    _description = 'Sale Order Line'

    book_price = fields.Float(
        string="Book Price", compute="compute_book_price", store=True)

    @api.depends('product_uom_qty', 'product_id.lst_price')
    def compute_book_price(self):
        for record in self:
            record.book_price = record.product_uom_qty * record.product_id.lst_price
