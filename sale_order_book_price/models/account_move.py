# -*- coding: utf-8 -*-

from odoo import models, fields, api


class account_move(models.Model):
    _name = 'account.move.line'
    _inherit = 'account.move.line'

    book_price = fields.Float(
        string="Book Price", compute="compute_book_price", store=True)

    @api.depends('quantity', 'product_id.lst_price')
    def compute_book_price(self):
        for record in self:
            record.book_price = record.quantity * record.product_id.lst_price
