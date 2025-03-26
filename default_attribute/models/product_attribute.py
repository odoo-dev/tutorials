# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    def write(self, vals):
        res = super().write(vals)
        if any(field in vals for field in ('value_ids', 'attribute_line_ids')):
            self.env['sale.order'].search([])._generate_global_info_lines()
        if 'value_ids' in vals:
            self._update_product_template_attribute_values()
        
        return res

    def _update_product_template_attribute_values(self):
        for attribute in self:
            products = self.env['product.template'].search([
                ('categ_id.default_attribute_ids', 'in', attribute.id)
            ])
            new_values = self.env['product.attribute.value'].search([
                ('attribute_id', '=', attribute.id)
            ]).ids
            for product in products:
                attr_line = product.attribute_line_ids.filtered(lambda line: line.attribute_id == attribute)
                attr_line.write({'value_ids': [(6, 0, new_values)]}) if attr_line else product.write({
                    'attribute_line_ids': [(0, 0, {
                        'attribute_id': attribute.id,
                        'value_ids': [(6, 0, new_values)]
                    })]
                })
