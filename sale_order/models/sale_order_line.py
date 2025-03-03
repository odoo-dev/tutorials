# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, fields, models


class SaleOrderLine(models.Model):
    _inherit = ['sale.order.line']

    divided_price = fields.Float("Divided Price")
    sale_tag_line_id = fields.Many2many('sale.order.line.tag', string='Tag')

    def unlink(self):
        for sale_line in self:
            sale_order_data = self.env['sale.order'].search(
                [('id', '=', sale_line.order_id.id)])
            tag_name = ''
            if sale_line.sale_tag_line_id:
                sale_order_line_wizard = self.env['sale.order.line.wizard'].search(
                    [('sale_order_line_id', '=', sale_line.id)])
                divided_sale_order_line = self.env['sale.order.line'].search(
                    [('id', '=', sale_order_line_wizard.sales_order_wizard_ids.divided_sale_order_line_id)])

                for tag in sale_line.sale_tag_line_id:
                    tag_name = f"{abs(sale_order_line_wizard.sales_order_wizard_ids.original_price - float(tag.name))}"

                tag = self.env['sale.order.line.tag'].create(
                    {'name': tag_name})
                divided_sale_order_line.sale_tag_line_id = [(4, tag.id)]

            else:
                for line_data in sale_order_data.order_line:
                    if line_data.sale_tag_line_id:
                        line_data.sale_tag_line_id = False

        return super().unlink()
