# -*- coding: utf-8 -*-

from odoo import models, fields


class StockPicking(models.Model):
    _name = 'stock.picking'
    _description = 'Stock Picking'
    _inherit = ['stock.picking']

    batch_info_ids = fields.One2many(
        'batch.information', 'picking_id', string='Batch Information')

    def button_validate(self):
        res = super().button_validate()
        arr = []
        for record in self:
            for move_lines in record.move_line_ids:
                arr.append({
                    'picking_id': record.id,
                    'product_id': move_lines.product_id.id,
                    'date_recipt': fields.Date.today(),
                })
        self.env['batch.information'].create(arr)
        return res
