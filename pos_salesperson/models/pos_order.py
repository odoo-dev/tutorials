# -*- coding: utf-8 -*-

from odoo import models, fields


class pos_order(models.Model):
    _name = 'pos.order'
    _inherit = 'pos.order'

    sales_person_id = fields.Many2one(
        'hr.employee', string='Salesperson')
