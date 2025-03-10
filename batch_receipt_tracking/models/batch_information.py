# -*- coding: utf-8 -*-

from odoo import models, fields


class BatchInformation(models.Model):
    _name = 'batch.information'
    _description = 'Batch Information'

    picking_id = fields.Many2one('stock.picking', string='Picking')
    product_id = fields.Many2one('product.product', string='Product')
    batch_number = fields.Char(string="Batch Number")
    date_recipt = fields.Date(string="Date of Receipt")
    date_expiry = fields.Date(string="Expiry Date")
    supplier_id = fields.Many2one('res.partner', string='Supplier', domain=[
                                  ('supplier_rank', '>', 0)])
    expiry_option = fields.Selection([
        ('not_available', 'Expiry Not Available'),
        ('after_opening', 'Expiry after opening the bottle')
    ], string='Expiry Option')
