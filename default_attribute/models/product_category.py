# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductCategory(models.Model):
    _inherit = 'product.category'
    _description = 'Product Category'

    show_global_info = fields.Boolean(string="Show on Global Info", default=False)
    defualt_attribute_id = fields.Many2many("product.attribute", string="Attributes")
