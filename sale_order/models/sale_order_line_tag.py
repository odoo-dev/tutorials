# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, fields, models


class SaleOrderTag(models.Model):
    _name = 'sale.order.line.tag'

    name = fields.Char('Name')
    color = fields.Integer(string='Sequence', default=1)
