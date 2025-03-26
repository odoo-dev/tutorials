# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model_create_multi
    def create(self, vals_list):
        products = super().create(vals_list)
        products._assign_default_attributes()
        return products

    def write(self, vals):
        res = super().write(vals)
        if 'categ_id' in vals:
            self._assign_default_attributes()
        return res

    def _assign_default_attributes(self):
        for product in self.filtered(lambda p: p.categ_id):
            default_attributes = product.categ_id.default_attribute_ids
            attr_lines = [
                (0, 0, {'attribute_id': attr.id, 'value_ids': [(6, 0, attr.value_ids.ids)]})
                for attr in default_attributes if attr.value_ids
            ]
            if not attr_lines:
                UserError(f"No valid attributes found for product '{product.name}' (ID: {product.id})")
            product.attribute_line_ids = [(5,)] + attr_lines
