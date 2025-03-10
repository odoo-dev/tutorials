# -*- coding: utf-8 -*-

from odoo import models, fields


class Product(models.Model):
    _name = 'product.product'
    _description = 'Product'
    _inherit = ['product.product']

    batch_info_ids = fields.One2many(
        'batch.information', 'product_id', string='Batch Information')
